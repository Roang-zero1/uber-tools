#!/usr/bin/env python3
"""
uber-tools

Usage:
  uber-tools bot
  uber-tools certificates
  uber-tools -h | --help
  uber-tools --version

Options:
  -h --help                         Show this screen.
  --version                         Show version.

Examples:
  uber-tools bot

Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/rdegges/skele-cli
"""

from inspect import getmembers, isclass

from docopt import docopt

from app import __version__ as VERSION


def main():
  """Main CLI entrypoint."""
  import app
  options = docopt(__doc__, version=VERSION)

  # Here we'll try to dynamically match the command the user is trying to run
  # with a pre-defined command class we've already created.
  for k, v in options.items():
    if hasattr(app, k) and v:
      module = getattr(app, k)
      commands = getmembers(module, isclass)
      command = [command[1] for command in commands if command[0] != 'Base'][0]
      command = command(options)
      command.run()

if __name__ == "__main__":
  #tools.setup.setup_logging()

  #this.config = tools.setup.loadconfig()
  #letools.configure(this.config)

  main()
