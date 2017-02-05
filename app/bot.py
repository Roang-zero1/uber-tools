"""
uber-tools bot subcommand

Usage:
  uber-tools bot

Options:
  -h --help                         Show this screen.
  --version                         Show version.

Examples:
  uber-tools bot

Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/rdegges/skele-cli
"""
import logging
import sys
from pprint import pprint
from time import sleep

from docopt import docopt

import telepot
import telepot.routing

import tools.le.cert as letools
import tools.setup


from app.base import Base

logger = logging.getLogger(__name__)
this = sys.modules[__name__]

class Bot(Base):
  """The telegram Bot"""

  def execute(self):
    tools.setup.setup_logging()

    this.config = tools.setup.loadconfig()
    letools.configure(this.config)

    if 'bot' in this.config:
      if 'key' in this.config['bot']:
        logger.info("Initializing the bot")
        this.bot = telepot.Bot(this.config['bot']['key'])
        if logger.isEnabledFor(logging.DEBUG):
          botdata = this.bot.getMe()
          logger.debug("Bot with id %d and name %s connected", botdata['id'], botdata['first_name'])
      else:
        logger.error("Bot configuration not found")
        exit(2)
    else:
      logger.error("Bot configuration not found")
      exit(2)

    main()

def listcerts(msg):
  cid = msg['chat']['id']
  domains = letools.getallcertinfo()
  output = "Information for {0} domains:\n".format(len(domains))
  for domain, domaininfo in domains.items():
    output += "• {0}\n".format(domain)
    output += "  • Valid until: {0}\n".format(domaininfo.valid_until)
    if len(domaininfo.alternates) > 1:
      output += "  • Alternates:\n"
      for alternate in domaininfo.alternates:
        output += "    • {}\n".format(alternate.value)
  this.bot.sendMessage(cid, output)
  pprint(msg)


def nothing(msg):
  cid = msg['chat']['id']
  this.bot.sendMessage(cid, 'Please use command interface!')


def handle(msg):
  table = {'listcert': listcerts, None: nothing}
  router = telepot.helper.Router(telepot.routing.by_chat_command(), table)
  router.route(msg)


def main():
  this.bot.message_loop(handle)
  while True:
    sleep(100000000)

if __name__ == "__main__":
  docopt(__doc__)
