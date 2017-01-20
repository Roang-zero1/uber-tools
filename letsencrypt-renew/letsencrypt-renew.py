import json
import logging
import logging.config
from sys import exit

from os import path, environ
from subprocess import check_output, STDOUT, CalledProcessError

from OpenSSL import crypto
from datetime import datetime, timedelta


def loadconfig():
  logger.info('Loading configuration')
  try:
    with open("config.json", encoding="utf-8") as fd:
      config = json.load(fd)
  except (FileNotFoundError, ValueError):
    logger.error("Logging configuration could not be read")
    exit(1)
  return config

def renewcert(domain):
  logger.info('Renewing certificate for domain {0}'.format(domain))
  domainc = config['domains'][domain]

  if config['general'].get('test',False): testing = '--staging'
  cmd = ['letsencrypt','certonly',testing,'-d {0}'.format(domain)]
  if 'alternates' in domainc:
      logger.debug('Renewing for alternate names {0}'.format(", ".join(domainc['alternates'])))
      for alternate in domainc['alternates']:
        cmd.append(' -d {0}'.format(alternate))
  
  cmd.append('--verbose')
  try:
    out = check_output(cmd, stderr=STDOUT)
    out = out.decode("utf-8")
  except CalledProcessError as e:
    print(e)
    out = e.output.decode("utf-8")
    logger.error(out)
    return
  logger.debug(out)

  with open(path.join(basepath,domain,'cert.pem')) as certf, \
       open(path.join(basepath,domain,'privkey.pem')) as keyf, \
       open(path.join(basepath,domain,'fullchain.pem')) as chainf, \
       open(path.join(basepath,domain,'combined.pem'),'w') as fullf:
    cert = certf.read()
    key = keyf.read()
    chain = chainf.read()
    fullf.write(key+ cert + chain)

  cmd = ['uberspace-add-certificate']
  cmd.append(' -k {0}'.format(path.join(basepath,domain,'privkey.pem')))
  cmd.append(' -c {0}'.format(path.join(basepath,domain,'cert.pem')))



def main():
  logger.info('Iniating certification renewal check')
  loadconfig()
  reneweddoms = 0

  for domain in config['domains']:
    logger.info('Verifying domain {0}'.format(domain))
    try:
      with open(path.join(basepath,domain,'cert.pem'), 'rt') as file:
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, file.read())
      certdate = datetime.strptime(cert.get_notAfter().decode('utf-8'), '%Y%m%d%H%M%SZ')
      validtime = certdate - datetime.utcnow()
    except:
      validtime = timedelta(0)
    if validtime < timedelta(days=config['general'].get('limit',15)):
      reneweddoms += 1
      renewcert(domain)
    else:
      logger.debug('Domain {0} will not be renewed'.format(domain))



if __name__ == "__main__":
  logging.basicConfig(level="INFO")
  logger = logging.getLogger(__name__)

  try:
    # set up proper logging. This one disables the previously configured loggers.
    with open("logging.json", "r", encoding="utf-8") as fd:
      logging.config.dictConfig(json.load(fd))
  except FileNotFoundError:
    logger.error("Logging configuration could not be read")

  config = loadconfig()
  basepath = basepath = config['general'].get("basepath",path.join(environ['HOME'],'.config/letsencrypt/live/'))

  main()
