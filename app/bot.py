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
  The full documentation can be found at:
    https://roang-zero1.github.io/uber-tools/
  For help using this tool, please open an issue on the Github repository:
    https://github.com/Roang-zero1/uber-tools
"""
import logging
from pprint import pprint
from time import sleep

import telepot
import telepot.routing

import app.tools.cert as letools
from app.base import Base

logger = logging.getLogger(__name__)

class Bot(Base):
  """The telegram Bot"""

  bot = None

  def execute(self):
    letools.configure(self.config)

    if 'bot' in self.config:
      if 'key' in self.config['bot']:
        logger.info("Initializing the bot")
        self.bot = telepot.Bot(self.config['bot']['key'])
        if logger.isEnabledFor(logging.DEBUG):
          botdata = self.bot.getMe()
          logger.debug("Bot with id %d and name %s connected", botdata['id'], botdata['first_name'])
      else:
        logger.error("Bot configuration not found")
        exit(2)
    else:
      logger.error("Bot configuration not found")
      exit(2)

    self.bot.message_loop(self.handle)
    while True:
      sleep(100000000)

  def listcerts(self, msg):
    cid = msg['chat']['id']
    domains = letools.getallcertinfo()
    output = "Information for {0} domains:\n".format(len(domains))
    for domain, domaininfo in domains.items():
      output += "• {0}\n".format(domain)
      output += "   Valid until: {0}\n".format(domaininfo.valid_until)
      if len(domaininfo.alternates) > 1:
        output += "   Alternates:\n"
        for alternate in domaininfo.alternates:
          output += "   • {}\n".format(alternate.value)
    self.bot.sendMessage(cid, output)
    pprint(msg)


  def nothing(self, msg):
    cid = msg['chat']['id']
    self.bot.sendMessage(cid, 'Please use command interface!')

  def handle(self, msg):
    table = {'listcert': self.listcerts, None: self.nothing}
    router = telepot.helper.Router(telepot.routing.by_chat_command(), table)
    router.route(msg)

if __name__ == "__main__":
  pass
