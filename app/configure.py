"""
uber-tools configure

Usage:
  uber-tools configure
  uber-tools configure bot
  uber-tools configure certificate

Options:
  -h --help                         Show this screen.
  --version                         Show version.

Examples:
  uber-tools bot

Help:
  The full documentation can be found at:
    https://roang-zero1.github.io/uber-tools/
  For help using this tool, please open an issue on the Github repository:
    https://github.com/Roang-zero1/uber-tools
"""
import logging
import sys

from app.base import Base

logger = logging.getLogger(__name__)
this = sys.modules[__name__]


class Configure(Base):

  def execute(self):
    print(self.args)
    raise NotImplementedError("Configure manually")

if __name__ == "__main__":
  pass
