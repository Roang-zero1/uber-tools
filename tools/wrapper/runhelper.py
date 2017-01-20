import logging

from collections import namedtuple
from subprocess import Popen, PIPE, CalledProcessError

CmdOutput = namedtuple('CmdOutput', 'out, err, retcode')
logger = logging.getLogger(__name__)

def runcmd(*popenargs, **kwargs):
    r"""Run command with arguments and return the std_out, std,err and
    returncode as a namedtuple.

    If the exit code was non-zero it raises a CalledProcessError.  The
    CalledProcessError object will have the return code in the returncode
    attribute and output in the output attribute.

    The arguments are the same as for the Popen constructor.  Example:

    >>> runcmd(["ls", "-l", "/dev/null"])
    CmdOutput(out='crw-rw-rw- 1 root root 1, 3 Nov  1 05:25 /dev/null\n', err='', retcode=0)

    The stdout and stderr argument is not allowed as it is used
    internally.

    >>> runcmd(["/bin/sh", "-c",
    ...               "ls -l non_existent_file ; exit 0"])
    CmdOutput(out='', err='ls: cannot access non_existent_file: No such file or directory\n', retcode=0)
    """
    cmd = kwargs.get("args")
    if cmd is None:
      cmd = popenargs[0]
    logger.debug("Executing command '{}'".format(cmd))

    if 'stdout' in kwargs:
      raise ValueError('stdout argument not allowed, it will be overridden.')
    if 'stdout' in kwargs:
      raise ValueError('stderr argument not allowed, it will be overridden.')
    process = Popen(stdout=PIPE, stderr=PIPE, *popenargs, **kwargs)
    std_out, std_err = process.communicate()
    retcode = process.poll()

    output = CmdOutput(std_out.decode("utf-8"),std_err.decode("utf-8"),retcode)

    if retcode:
        raise CalledProcessError(retcode, cmd, output=output)
    return output
