import json
import logging
import logging.config
from sys import exit

from bs4 import BeautifulSoup

from os import path, environ
from subprocess import check_output

from OpenSSL import crypto
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

def newtag(type,text):
  tag = htmlbody.new_tag(type)
  tag.string = text
  return tag

def loadconfig():
  logger.info('Loading configuration')
  try:
    with open("config.json", encoding="utf-8") as fd:
      config = json.load(fd)
  except (FileNotFoundError, ValueError):
    logger.error("Logging configuration could not be read")
    exit(1)
  return config

def renewcert(domain,domtag):
  logger.info('Renewing certificate for domain {0}'.format(domain))
  domainc = config['domains'][domain]

  sumtag = newtag('p','Rewing certificate for domain {0}'.format(domain))
  domtag.insert(len(domtag),sumtag)

  if config['general'].get('test',False): testing = '--staging'
  cmd = ['letsencrypt','certonly',testing,'-d {0}'.format(domain)]
  if 'alternates' in domainc:
      logger.debug('Renewing for alternate names {0}'.format(", ".join(domainc['alternates'])))
      sumtag.append('with alternates:')
      ultag = htmlbody.new_tag('ul')
      sumtag.insert_after(ultag)
      for alternate in domainc['alternates']:
        litag = htmlbody.new_tag('li')
        litag.string = alternate
        ultag.append(litag)
        cmd.append(' -d {0}'.format(alternate))
      
  else:
    sumtag.append('.')
  domtag.insert(len(domtag),newtag('h3','Renewing Certificate'))
  domtag.insert(len(domtag),newtag('pre',' '.join(cmd)))
  print(' '.join(cmd))
  out = check_output(cmd)
  print(out)
  domtag.insert(len(domtag),newtag('pre',' '.join(out)))

  with open(path.join(basepath,domain,'cert.pem')) as certf, \
       open(path.join(basepath,domain,'privkey.pem')) as keyf, \
       open(path.join(basepath,domain,'fullchain.pem')) as chainf, \
       open(path.join(basepath,domain,'combined.pem'),'w') as fullf:
    cert = certf.read()
    key = keyf.read()
    chain = chainf.read()
    fullf.write(key+ cert + chain)
    domtag.insert(len(domtag),newtag('p','Joined certificate successfuly as combined.pem'))

  domtag.insert(len(domtag),newtag('h3','Updating webserver'))
  cmd = ['uberspace-add-certificate']
  cmd.append(' -k {0}'.format(path.join(basepath,domain,'privkey.pem')))
  cmd.append(' -c {0}'.format(path.join(basepath,domain,'cert.pem')))
  domtag.insert(len(domtag),newtag('pre',' '.join(cmd)))



def main():
  logger.info('Iniating certification renewal check')
  loadconfig()
  htmlbody.find(id='date').string = \
        datetime.now().replace(microsecond=0).isoformat(sep=' ')
  htmlbody.find(id='domnum').string = str(len(config['domains']))

  reneweddoms = 0

  for domain in config['domains']:
    domtag = htmlbody.new_tag('div')
    domtag.append(newtag('h2','{0}'.format(domain)))
    htmlbody.find(id='domains').append(domtag)
    logger.info('Verifying domain {0}'.format(domain))
    try:
      with open(path.join(basepath,domain,'cert.pem'), 'rt') as file:
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, file.read())
      certdate = datetime.strptime(cert.get_notAfter().decode('utf-8'), '%Y%m%d%H%M%SZ')
      validtime = certdate - datetime.utcnow()
    except:
      validtime = timedelta(0)
    if validtime < timedelta(days=config['general'].get('limit',15)):
      reneweddoms += 1
      renewcert(domain,domtag)
    else:
      logger.debug('Domain {0} will not be renewed'.format(domain))
      domtag.insert(len(domtag),newtag('p','Not renewed as this certificate is still valid for {0}'.format(validtime)))

  htmlbody.find(id='rnum').string = str(reneweddoms)

  print(htmlbody.prettify())
  if 'mail' in config:
      mailconf = config['mail']
      if all(val in mailconf for val in ("from","to","password")):
        msg = MIMEMultipart('alternative')
        msg.attach(MIMEText(htmlbody.get_text(), 'plain'))
        msg.attach(MIMEText(htmlbody.prettify(), 'html'))
        msg['Subject'] = 'Certificate renewal notice'
        msg['From'] = mailconf['from']
        msg['BCC'] = ", ".join(mailconf['to'])

        s = smtplib.SMTP('localhost',587)
        #s.set_debuglevel(1)
        s.starttls()

        s.login(mailconf['from'],mailconf['password'])
        s.send_message(msg)
        s.quit()

if __name__ == "__main__":
  logging.basicConfig(level="INFO")
  logger = logging.getLogger()

  try:
    # set up proper logging. This one disables the previously configured loggers.
    with open("logging.json", "r", encoding="utf-8") as fd:
      logging.config.dictConfig(json.load(fd))

  except FileNotFoundError:
    logger.error("Logging configuration could not be read")

  config = loadconfig()
  basepath = basepath = config['general'].get("basepath",path.join(environ['HOME'],'.config/letsencrypt/live/'))

  with open("renewal.html", encoding="utf-8") as fd:
    htmlbody = BeautifulSoup(fd, "html.parser")

  main()
