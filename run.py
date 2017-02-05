#!/usr/bin/env python3
"""
uber-tools

Usage: uber-tools [--version] [--help]
                  <command> [<args>...]

Options:
  -h --help                         Show this screen.
  --version                         Show version.

Available uber-tools commands:
  bot
  certificate

Examples:
  uber-tools bot

Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/rdegges/skele-cli
"""

from docopt import DocoptExit, docopt

from app import __version__ as VERSION

def main():
  """Main CLI entrypoint."""
  import app
  args = docopt(__doc__, version=VERSION, options_first=True)

   # Retrieve the command to execute.
  command_name = args.pop('<command>').capitalize()

  # Retrieve the command arguments.
  command_args = args.pop('<args>')
  if command_args is None:
    command_args = {}

  # After 'poping' '<command>' and '<args>', what is left in the args dictionary are the global arguments.

  # Retrieve the class from the 'commands' module.
  try:
    command_class = getattr(app, command_name)
  except AttributeError:
    print("Unknown command '{}'.".format(command_name))
    raise DocoptExit()

  # Create an instance of the command.
  command = command_class(command_args, args)

  # Execute the command.
  command.execute()

if __name__ == "__main__":
  #tools.setup.setup_logging()

  #this.config = tools.setup.loadconfig()
  #letools.configure(this.config)

  main()
