#!/usr/bin/env python
"""
Drafter builds Gmail drafts for you programmatically.
    - inspired by previous work by @samplebias on Stack Overflow and @jsha (Jacob Hoffman-Andrews)
        * http://stackoverflow.com/questions/5355067/programatically-save-draft-in-gmail-drafts-folder
        * https://jacob.hoffman-andrews.com/README/index.php/2012/03/27/easy-custom-mail-merge-with-python-and-gmail/
    - read README for setup and usage details
    - Drafter takes a CSV file with headers and a Mustache template and saves a set of drafts in your Gmail account
"""

import email.message
import random
import time
import os
import yaml
import oauth2 as oauth
import oauth2.clients.imap as imaplib

# Configuration and static variables
def open_yaml(f):
    return open(os.path.join(os.path.dirname(os.path.realpath(__file__)), f))
try:
    config = yaml.load(open_yaml('config.yaml'))
except IOError:
    print "config.yaml missing-- no configuration file found (see config.example.yaml for a sample configuration.)"
    sys.exit()

# Set up a three-legged OAuth request
consumer = oauth.Consumer('anonymous','anonymous')
token = oauth.Token(config['token'], config['secret'])
url = "https://mail.google.com/mail/b/%s/imap/" % config['email'] # URL for Google's XOAUTH

# Connect to Gmail's IMAP service
conn = imaplib.IMAP4_SSL('imap.googlemail.com')
conn.debug = 4
conn.authenticate(url, consumer, token)
imap = imaplib.imaplib

# Create the message
msg = email.message.Message()
msg['Subject'] = 'subject of the message'
msg['From'] = config['email']
msg['To'] = config['email']
msg.set_payload('Body of the message')

# Add the message to Gmail's drafts folder
now = imap.Time2Internaldate(time.time())
conn.append('[Gmail]/Drafts', '', now, str(msg))

conn.logout()
