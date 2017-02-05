"""
uber-tools certificate subcommand

Usage:
  uber-tools certificate renew [-f] [--staging] (all|<domain>...)
  uber-tools certificate info (all|<domain>...)

Options:
  -f --force                        Force certificate renewal.
  -h --help                         Show this screen.
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

import app.tools.cert as letools
from app.base import Base

logger = logging.getLogger(__name__)
this = sys.modules[__name__]


class Certificate(Base):
  """The telegram Bot"""

  def execute(self):
    letools.configure(self.config, staging=self.args['--staging'])

    if self.args['renew']:
      # TODO: Implement certificate renewal
      if self.args['all']:
        raise NotImplementedError("Renewing all domains")
      else:
        raise NotImplementedError(
            "Renewing domains {}".format(self.args['<domain>']))
    elif self.args['info']:
      # TODO: Implement certificate information gathering
      if self.args['all']:
        domains = letools.getallcertinfo()
        for domain in domains:
          logger.info("Domaininfo for %s", letools.getcertinfo(domain))
      else:
        for domain in self.args['<domain>']:
          logger.info("Domaininfo for %s", letools.getcertinfo(domain))
    else:
      raise NotImplementedError("Requested command not implemented")

if __name__ == "__main__":
  pass
