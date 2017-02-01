"""
Custom wrapper for the :func:`subprocess.Popen` function
"""
import logging

from collections import namedtuple
from subprocess import Popen, PIPE, CalledProcessError

CmdOutput = namedtuple('CmdOutput', 'out, err, retcode')
"""
The command stdout and stderr buffer content and the returncode.

"""
logger = logging.getLogger(__name__)

def runcmd(*popenargs, **kwargs):
  r"""Run command with arguments and return the std_out, std,err and
  returncode as a namedtuple.

  If the exit code was non-zero it raises a CalledProcessError.  The
  CalledProcessError object will have the return code in the returncode
  attribute and output in the output attribute.

  The arguments are the same as for the Popen constructor.
  The stdout and stderr argument is not allowed as they are used internally.

  Args:
    *args: Variable length argument list.
    **kwargs: Arbitrary keyword arguments.

  Returns:
    CmdOutput: The output created by the executed command.

  Example:
    >>> runcmd(["ls", "-l", "/dev/null"])

  """
  cmd = kwargs.get("args")
  if cmd is None:
    cmd = popenargs[0]
  logger.debug("Executing command '%s'", cmd)

  if 'stdout' in kwargs:
    raise ValueError('stdout argument not allowed, it will be overridden.')
  if 'stdout' in kwargs:
    raise ValueError('stderr argument not allowed, it will be overridden.')
  process = Popen(stdout=PIPE, stderr=PIPE, *popenargs, **kwargs)
  std_out, std_err = process.communicate()
  retcode = process.poll()

  output = CmdOutput(std_out.decode("utf-8"), std_err.decode("utf-8"), retcode)

  if retcode:
    raise CalledProcessError(retcode, cmd, output=output)
  return output
