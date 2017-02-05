# skele/commands/base.py
"""
The base command.
"""

from sys import modules
from docopt import docopt

class Base(object):
  """
  A base command.
  """

  def __init__(self, command_args, global_args):
    """
    Initialize the command

    Args:
      command_args: arguments of the command
      global_args: arguments of the program
    """
    self.args = docopt(modules[self.__module__].__doc__, argv=command_args or {})
    self.global_args = global_args or {}

  def execute(self):
    """
    The function running the command in the implementing class
    """
    raise NotImplementedError('You must implement the run() method yourself!')
