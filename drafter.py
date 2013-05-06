#!/usr/bin/env python
"""
Drafter is command-line mail merge: it builds Gmail drafts for you programmatically.
    - Drafter takes a CSV file with headers and a Mustache template and saves a set of drafts in your Gmail account
    - inspired by work of @samplebias on Stack Overflow and @jsha (Jacob Hoffman-Andrews)
        * http://stackoverflow.com/questions/5355067/programatically-save-draft-in-gmail-drafts-folder
        * https://jacob.hoffman-andrews.com/README/index.php/2012/03/27/easy-custom-mail-merge-with-python-and-gmail/
    - read README for setup and usage details
"""

import random
import time
import os, sys
import argparse
import re
import oauth2 as oauth
import oauth2.clients.imap as imaplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import csv
import markdown
import pystache
import yaml
from premailer import transform

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

# Read in and process the configuration
def open_yaml(f):
    return open(os.path.join(os.path.dirname(os.path.realpath(__file__)), f))
try:
    config = yaml.load(open_yaml('config.yaml'))
except IOError:
    print "config.yaml missing-- no configuration file found (see config.example.yaml for a sample configuration.)"
    sys.exit()

# Read in and process the YAML / Markdown / Mustache template. This whole approach is messy and bad but works
try:
    f = open_yaml(args.template)
    template_raw = f.readlines()

    yaml_front_matter = ''
    message_template = ''

    reading_yaml_fm = False
    reading_document = False
    trimmed_leading_whitespace = False

    for line in template_raw:
        if not reading_document:
            # Skip blank lines
            if not line.strip():
                continue

            # If we're already reading in the YAML front matter...
            if reading_yaml_fm:
                # Check if we've hit the closing tag for the YAML front matter
                if line.rstrip().startswith('---'):
                    reading_yaml_fm = False
                else:
                    # This line is YAML, so keep it
                    yaml_front_matter += line
                continue

            # Look for an opening tag for the YAML front matter
            if line.rstrip().startswith('---'):
                reading_yaml_fm = True
                continue
            # If it's not at the start of the file, we're now reading the document
            else:
                reading_document = True

        if reading_document:
            # This line is the message, so keep it
            message_template += line

    template = {}
    if len(yaml_front_matter) > 0:
        template.update(yaml.load(yaml_front_matter))
    
    # We're adding a custom style (embedded inline with Premailer) so that the first paragraph doesn't have a leading margin-top
    template['message'] = transform("""
        <html>
            <style type="text/css">
                p:first-child { margin-top: 0; }
            </style>
            %s
        </html>
    """ % markdown.markdown(message_template))

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
