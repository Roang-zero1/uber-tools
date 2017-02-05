"""
uber-tools certificate subcommand

Usage:
  uber-tools certificate renew [-f] [--testing | --staging] (all|<domain>)
  uber-tools certificate info (all|<domain>)

Options:
  -f --force                        Force certificate renewal.
  -h --help                         Show this screen.
  --testing                         Receive certificate to memory only.
  --staging                         Receive certificate from staging server.
  --version                         Show version.

Examples:
  uber-tools certificate

Help:
  The full documentation can be found at:
    https://roang-zero1.github.io/uber-tools/
  For help using this tool, please open an issue on the Github repository:
    https://github.com/Roang-zero1/uber-tools
"""

import logging
import sys
from datetime import datetime, timedelta

import app.tools.cert as letools
from app.base import Base

logger = logging.getLogger(__name__)
this = sys.modules[__name__]

class Certificate(Base):
  """The telegram Bot"""

  def execute(self):
    letools.configure(self.config)
    print(self.config)

    if self.args['renew']:
      raise NotImplementedError("Renewing {}".format(self.args['<domain>'] or self.args['all']))
    elif self.args['info']:
      raise NotImplementedError("Printing information for {}".format(self.args['<domain>'] or self.args['all']))
    else:
      raise NotImplementedError("Requested command not implemented")


    logger.info('Iniating certification renewal check')
    reneweddoms = 0

    domains = letools.getallcertinfo()

    for domain in self.config['domains']:
      logger.info('Verifying domain %s', domain)
      renew = False
      if domain in domains:
        validtime = domains[domain].valid_until  - datetime.utcnow()
        if validtime < timedelta(days=self.config['general'].get('limit', 15)):
          renew = True
      else:
        renew = True

      if renew:
        reneweddoms += 1
        letools.renewcert(domain)
      else:
        logger.debug('Domain %s will not be renewed', domain)

if __name__ == "__main__":
  pass
