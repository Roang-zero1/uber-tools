#!/usr/bin/env python3

import logging
import sys
from datetime import datetime, timedelta

import tools.le.cert as letools
import tools.setup

logger = logging.getLogger(__name__)
this = sys.modules[__name__]

def main():
  logger.info('Iniating certification renewal check')
  reneweddoms = 0

  domains = letools.getallcertinfo()

  for domain in this.config['domains']:
    logger.info('Verifying domain %s', domain)
    renew = False
    if domain in domains:
      validtime = domains[domain].valid_until  - datetime.utcnow()
      if validtime < timedelta(days=this.config['general'].get('limit', 15)):
        renew = True
    else:
      renew = True

    if renew:
      reneweddoms += 1
      letools.renewcert(domain)
    else:
      logger.debug('Domain %s will not be renewed', domain)

if __name__ == "__main__":
  tools.setup.setup_logging()

  this.config = tools.setup.loadconfig()
  letools.configure(this.config)

  main()
