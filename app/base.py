# skele/commands/base.py
"""
The base command.
"""

class Base(object):
  """
  A base command.
  """

  def __init__(self, options, *args, **kwargs):
    self.options = options
    self.args = args
    self.kwargs = kwargs

  def run(self):
    """
    The function running the command in the implementing class
    """
    raise NotImplementedError('You must implement the run() method yourself!')
