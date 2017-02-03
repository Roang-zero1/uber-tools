"""
Let's encrypt certiciation tools

This module provides tools to check and renew certificates on the uberspace hostinprovider.

"""

import logging
import sys
from collections import namedtuple
from os import environ, listdir, path
from subprocess import CalledProcessError

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import ExtensionOID

from tools.wrapper.runhelper import runcmd

this = sys.modules[__name__]
this.config = {}
this.basepath = ""
logger = logging.getLogger(__name__)

CertInfo = namedtuple('CertInfo', 'domain, valid_until, alternates')


def configure(configuration):
  """Set configuration for this module"""
  this.config = configuration
  this.basepath = this.config['general'].get(
      "basepath", path.join(environ['HOME'], '.config/letsencrypt/live/'))


def getcertinfo(directory):
  """Get the information of the certificate in the 'directory'"""
  with open(path.join(this.basepath, directory, 'cert.pem'), 'rb') as file:
    content = file.read()
  cert = x509.load_pem_x509_certificate(content, default_backend())
  alternates = cert.extensions.get_extension_for_oid(
      ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value
  return CertInfo(cert.subject, cert.not_valid_after, alternates)


def getallcertinfo():
  """Get the information of all certicicates directories below basepath"""
  domains = {}
  dirs = listdir(this.basepath)
  for directory in dirs:
    domains[directory] = getcertinfo(directory)
  return domains


def renewcert(domain):
  """Renew the certificate for a given domain"""
  logger.info('Renewing certificate for domain %s', domain)
  domainc = this.config['domains'][domain]

  if this.config['general'].get('test', False):
    testing = '--staging'
  cmd = ['letsencrypt', 'certonly', testing, '-d {0}'.format(domain)]
  if 'alternates' in domainc:
    logger.debug('Renewing for alternate names %s',
                 ", ".join(domainc['alternates']))
    for alternate in domainc['alternates']:
      cmd.append(' -d {0}'.format(alternate))

  try:
    output = runcmd(cmd)
    logger.info('Certificate renewal successful')
  except CalledProcessError as ex:
    output = ex.output
    logger.error('Certificate renewal failed.\n%s', output.err)
    return
  if output.err:
    logger.debug(output.err)

  logger.info("Creating a full certificate file")
  with open(path.join(this.basepath, domain, 'cert.pem')) as certf, \
          open(path.join(this.basepath, domain, 'privkey.pem')) as keyf, \
          open(path.join(this.basepath, domain, 'fullchain.pem')) as chainf, \
          open(path.join(this.basepath, domain, 'combined.pem'), 'w') as fullf:
    cert = certf.read()
    key = keyf.read()
    chain = chainf.read()
    fullf.write(key + cert + chain)

  logger.info("Add certificate to webserver")
  cmd = ['uberspace-add-certificate']
  cmd.append(' -k {0}'.format(path.join(this.basepath, domain, 'privkey.pem')))
  cmd.append(' -c {0}'.format(path.join(this.basepath, domain, 'cert.pem')))

if __name__ == "__main__":
  pass
