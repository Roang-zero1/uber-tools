import json
import logging
import logging.config
import tools.logging

from os import path, environ
from datetime import datetime, timedelta

import tools.le.cert as letools

def loadconfig():
  logger.info('Loading configuration')
  try:
    with open("config.json", encoding="utf-8") as fd:
      config = json.load(fd)
  except (FileNotFoundError, ValueError) as e:
    logger.error("Logging configuration could not be read:\n{}".format(e))
    exit(1)
  return config

def main():
  logger.info('Iniating certification renewal check')
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
      letools.renewcert(domain)
    else:
      logger.debug('Domain {0} will not be renewed'.format(domain))
  
if __name__ == "__main__":
  tools.logging.setup_logging()
  logger = logging.getLogger(__name__)

  config = loadconfig()
  letools.configure(config)

  main()
