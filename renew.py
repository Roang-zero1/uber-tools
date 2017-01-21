import logging
import tools.logging
import tools.configuration

from os import path, environ
from datetime import datetime, timedelta

from OpenSSL import crypto

import tools.le.cert as letools

logger = logging.getLogger(__name__)

def main():
  logger.info('Iniating certification renewal check')
  reneweddoms = 0

  domains = letools.getcertinfo()

  for domain in config['domains']:
    logger.info('Verifying domain {0}'.format(domain))
    try:
      with open(path.join(basepath,domain,'cert.pem'), 'rt') as file:
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, file.read())
      certdate = datetime.strptime(cert.get_notAfter().decode('utf-8'), '%Y%m%d%H%M%SZ')
      validtime = certdate - datetime.utcnow()
    except FileNotFoundError as ex:
      validtime = timedelta(0)
    if validtime < timedelta(days=config['general'].get('limit',15)):
      reneweddoms += 1
      letools.renewcert(domain)
    else:
      logger.debug('Domain {0} will not be renewed'.format(domain))

if __name__ == "__main__":
  tools.logging.setup_logging()

  config = tools.configuration.loadconfig()
  basepath = basepath = config['general'].get("basepath",path.join(environ['HOME'],'.config/letsencrypt/live/'))
  letools.configure(config)

  main()
