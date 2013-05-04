#!/usr/bin/env python
"""
Drafter builds Gmail drafts for you programmatically.
    - inspired by previous work by @samplebias on Stack Overflow and @jsha (Jacob Hoffman-Andrews)
        * http://stackoverflow.com/questions/5355067/programatically-save-draft-in-gmail-drafts-folder
        * https://jacob.hoffman-andrews.com/README/index.php/2012/03/27/easy-custom-mail-merge-with-python-and-gmail/
    - read README for setup and usage details
    - Drafter takes a CSV file with headers and a Mustache template and saves a set of drafts in your Gmail account
"""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import time
import os, sys
import yaml
import oauth2 as oauth
import oauth2.clients.imap as imaplib
import argparse
import csv
import pystache
import re

# Elegant solution for a CSV parser that supports encodings, taken from http://stackoverflow.com/questions/5478659/python-module-like-csv-dictreader-with-full-utf8-support
def UnicodeDictReader(str_data, encoding, **kwargs):
    csv_reader = csv.DictReader(str_data, **kwargs)
    # Decode the keys once
    keymap = dict((k, k.decode(encoding)) for k in csv_reader.fieldnames)
    for row in csv_reader:
        yield dict((keymap[k], v.decode(encoding)) for k, v in row.iteritems())

# Alias imaplib since we're using OAuth2's imaplib wrapper
imap = imaplib.imaplib

# Command-line arguments: we specify the template and the CSV data file on the command line
parser = argparse.ArgumentParser(description='Drafter builds Gmail drafts for you programmatically.')
parser.add_argument('-t', '--template', help='Mustache template for email that will be generated (see example_message.mustache for an example)', required=True)
parser.add_argument('-d', '--csv-data', help='CSV data file with headers for the template (see example_data.csv for an example)', required=True)
args = parser.parse_args()

# Configuration and static variables
def open_yaml(f):
    return open(os.path.join(os.path.dirname(os.path.realpath(__file__)), f))
try:
    config = yaml.load(open_yaml('config.yaml'))
except IOError:
    print "config.yaml missing-- no configuration file found (see config.example.yaml for a sample configuration.)"
    sys.exit()

try:
    template = yaml.load(open_yaml(args.template))
except IOError:
    print "Could not read the specified template: %s" % args.template
    sys.exit()

def send_message(conn, template_data):
    d = template_data

    # Create the message
    msg = MIMEMultipart('alternative')
    if 'subject' in template:
        msg['Subject'] = pystache.render(template['subject'], d)
    if 'from' in template:
        msg['From'] = pystache.render(template['from'], d)
    if 'to' in template:
        msg['To'] = pystache.render(template['to'], d)
    if 'cc' in template:
        msg['Cc'] = pystache.render(template['cc'], d)
    if 'bcc' in template:
        msg['Bcc'] = pystache.render(template['bcc'], d)

    # We have to attach the body of the message as both text/plain and
    # text/html, and attach each part to the message container
    body = pystache.render(template['message'], d)
    print body
    plain_part = MIMEText(re.sub('<[^<]+?>', '', body), 'plain', 'utf-8')
    html_part = MIMEText(body, 'html', 'utf-8')

    msg.attach(plain_part)
    msg.attach(html_part)

    # Add the message to Gmail's drafts folder
    now = imap.Time2Internaldate(time.time())
    conn.append('[Gmail]/Drafts', '', now, str(msg))

# Set up a three-legged OAuth request
consumer = oauth.Consumer('anonymous','anonymous')
token = oauth.Token(config['token'], config['secret'])
url = "https://mail.google.com/mail/b/%s/imap/" % config['email'] # URL for Google's XOAUTH

# Connect to Gmail's IMAP service and create our drafts
conn = imaplib.IMAP4_SSL('imap.googlemail.com')
conn.debug = 4
conn.authenticate(url, consumer, token)

# Build and send the emails
try:
    reader = UnicodeDictReader(open(args.csv_data), delimiter=',', encoding='utf-8')
except IOError:
    print "Could not read the specified CSV data file: %s" % args.csv_data
    sys.exit()
rows = list(reader)
total_rows = len(rows)
for i, row in enumerate(rows):
    print "[%d/%d] Created draft" % (i+1, total_rows)
    send_message(conn, row)
    time.sleep(1)

conn.logout()
