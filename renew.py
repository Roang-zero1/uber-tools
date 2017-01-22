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

  domains = letools.getallcertinfo()

  for domain in config['domains']:
    logger.info('Verifying domain {0}'.format(domain))
    renew = False
    if domain in domains:
      validtime = domains[domain].valid_until  - datetime.utcnow()
      if validtime < timedelta(days=config['general'].get('limit',15)):
        renew = True
    else:
      renew = True

    if renew:
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
