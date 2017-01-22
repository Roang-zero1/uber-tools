import logging

from os import path, environ, listdir
from collections import namedtuple
from tools.wrapper.runhelper import runcmd
from subprocess import CalledProcessError

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import ExtensionOID

config = {}
basepath = ""
logger = logging.getLogger(__name__)

domainInfo = namedtuple('DomainInfo', 'domain, valid_until, alternates')

def configure(configuration):
  global config, basepath

  config = configuration
  basepath = basepath = config['general'].get("basepath",path.join(environ['HOME'],'.config/letsencrypt/live/'))

def getcertinfo(directory):
  with open(path.join(basepath,directory,'cert.pem'), 'rb') as file:
    content = file.read()
  cert = x509.load_pem_x509_certificate(content, default_backend())
  alternates=cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value
  return domainInfo(cert.subject,cert.not_valid_after,alternates)

def getallcertinfo():
  domains = {}
  dirs = listdir(basepath)
  for directory in dirs:
    domains[directory] = getcertinfo(directory)
  return domains

def renewcert(domain):
  logger.info('Renewing certificate for domain {0}'.format(domain))
  domainc = config['domains'][domain]

  if config['general'].get('test',False): testing = '--staging'
  cmd = ['letsencrypt','certonly',testing,'-d {0}'.format(domain)]
  if 'alternates' in domainc:
    logger.debug('Renewing for alternate names {0}'.format(", ".join(domainc['alternates'])))
    for alternate in domainc['alternates']:
      cmd.append(' -d {0}'.format(alternate))

  try:
    output = runcmd(cmd)
    logger.info('Certificate renewal successful')
  except CalledProcessError as e:
    output = e.output
    logger.error('Certificate renewal failed.\n{}'.format(output.err))
    return
  if output.err:
    logger.debug(output.err)

  logger.info("Creating a full certificate file")
  with open(path.join(basepath,domain,'cert.pem')) as certf, \
       open(path.join(basepath,domain,'privkey.pem')) as keyf, \
       open(path.join(basepath,domain,'fullchain.pem')) as chainf, \
       open(path.join(basepath,domain,'combined.pem'),'w') as fullf:
    cert = certf.read()
    key = keyf.read()
    chain = chainf.read()
    fullf.write(key+ cert + chain)

  logger.info("Add certificate to webserver")
  cmd = ['uberspace-add-certificate']
  cmd.append(' -k {0}'.format(path.join(basepath,domain,'privkey.pem')))
  cmd.append(' -c {0}'.format(path.join(basepath,domain,'cert.pem')))

if __name__ == "__main__":
  pass
