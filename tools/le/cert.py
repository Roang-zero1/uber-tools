import logging

from os import path, environ

from tools.wrapper.runhelper import runcmd
from subprocess import CalledProcessError

config = {}
basepath = ""
logger = logging.getLogger(__name__)

def configure(configuration):
    global config, basepath

    config = configuration
    basepath = basepath = config['general'].get("basepath",path.join(environ['HOME'],'.config/letsencrypt/live/'))

def renewcert(domain):
  logger.info('Renewing certificate for domain {0}'.format(domain))
  domainc = config['domains'][domain]

  if config['general'].get('test',False): testing = '--staging'
  cmd = ['letsencrypt','certonly',testing,'-d {0}'.format(domain)]
  if 'alternates' in domainc:
      logger.debug('Renewing for alternate names {0}'.format(", ".join(domainc['alternates'])))
      for alternate in domainc['alternates']:
        cmd.append(' -d {0}'.format(alternate))
  
  try:
    output = runcmd(cmd)
    logger.info('Certificate renewal successful')
  except CalledProcessError as e:
    output = e.output
    logger.error('Certificate renewal failed.\n{}'.format(output.err))
    return  
  if output.err:
    logger.debug(output.err)
  
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

if __name__ == "__main__":
  pass
