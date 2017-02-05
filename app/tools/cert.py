"""
Let's encrypt certiciation tools

This module provides tools to check and renew certificates on the uberspace hostinprovider.

"""
import logging
import sys
from collections import namedtuple
from datetime import datetime, timedelta
from os import R_OK, access, environ, listdir, path
from subprocess import CalledProcessError

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import ExtensionOID, NameOID
from validators.domain import domain as validate_domain

from app.tools.runhelper import runcmd

this = sys.modules[__name__]
this.config = {}
this.basepath = ""
logger = logging.getLogger(__name__)


class CertInfo(namedtuple("CertInfo", ["domain", "valid_until", "alternates"])):
  """
  Information for one Certificate

  Attributes:
    domain: The subject common name for the certificate.
    valid_until: Validity time of the certificate.
    alternates: Alternate subject names of the certificate.
  """
  __slots__ = ()

  def __str__(self):
    output = "{0}\n".format(self.domain)
    output += "   Valid until: {0}".format(self.valid_until)
    if len(self.alternates) > 1:
      output += "\n   Alternates:\n"
      for alternate in self.alternates[:-1]:
        output += "   • {}\n".format(alternate)
      output += "   • {}".format(self.alternates[-1])
    return output


class DomainNotFound(Exception):
  pass


class InvalidDomain(Exception):
  pass


def configure(configuration, staging=False):
  """
  Set configuration for this module

  Args:
    configuration: The application configuration to be set for the certificat tools.
    staging: Should certificates be requested from the staging environment.
  """
  this.config = configuration
  this.staging = staging
  this.basepath = this.config['general'].get(
      "basepath", path.join(environ['HOME'], '.config/letsencrypt/live/'))


def getcertinfo(domain, recurse=True):
  """Get the information of the certificate for the domain"""
  if not validate_domain(domain):
    raise InvalidDomain("Domain {} not properly formated.".format(domain))
  if access(path.join(this.basepath, domain, 'cert.pem'), R_OK):
    with open(path.join(this.basepath, domain, 'cert.pem'), 'rb') as file:
      content = file.read()
    cert = x509.load_pem_x509_certificate(content, default_backend())
    common_name = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[
        0].value
    alternates = []
    for alternate in cert.extensions.get_extension_for_oid(
            ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value:
      alternates.append(alternate.value)
    return CertInfo(common_name, cert.not_valid_after, alternates)
  elif recurse:
    domains = getallcertinfo()
    for domaininfo in domains.values():
      if domain in domaininfo.alternates:
        return domaininfo
  raise DomainNotFound(
      "The domain {} certificate was not found".format(domain))


def getallcertinfo():
  """Get the information of all certicicates directories below basepath"""
  domains = {}
  dirs = listdir(this.basepath)
  for directory in dirs:
    domains[directory] = getcertinfo(directory, recurse=False)
  return domains


def renewallcertificates():
  # TODO: Implement certificate renewal for all domains
  logger.info('Iniating certification renewal check')
  reneweddoms = 0

  domains = getallcertinfo()

  for domain in this.config['domains']:
    logger.info('Verifying domain %s', domain)
    renew = False
    if domain in domains:
      validtime = domains[domain].valid_until - datetime.utcnow()
      if validtime < timedelta(days=this.config['general'].get('limit', 15)):
        renew = True
    else:
      renew = True

    if renew:
      reneweddoms += 1
      renewcert(domain)
    else:
      logger.debug('Domain %s will not be renewed', domain)


def renewcert(domain):
  # TODO: Reimplement certificate renewal
  """Renew the certificate for a given domain"""
  logger.info('Renewing certificate for domain %s', domain)
  domainc = this.config['domains'][domain]

  # TODO: Add staging directory
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

  # TODO: Skip this in staging
  logger.info("Add certificate to webserver")
  cmd = ['uberspace-add-certificate']
  cmd.append(' -k {0}'.format(path.join(this.basepath, domain, 'privkey.pem')))
  cmd.append(' -c {0}'.format(path.join(this.basepath, domain, 'cert.pem')))

  # TODO: Run additional commands after certificate has been created

if __name__ == "__main__":
  pass
