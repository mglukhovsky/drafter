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
import imaplib
import random
import time
import xoauth
import os
import yaml

# Configuration and static variables
def open_yaml(f):
    return open(os.path.join(os.path.dirname(os.path.realpath(__file__)), f))
try:
    config = yaml.load(open_yaml('config.yaml'))
except IOError:
    print "config.yaml missing-- no configuration file found (see config.example.yaml for a sample configuration.)"
    sys.exit()

# Construct the OAuth access token
nonce = str(random.randrange(2**64 - 1))
timestamp = str(int(time.time()))
consumer = xoauth.OAuthEntity('anonymous', 'anonymous')
access = xoauth.OAuthEntity(config['token'], config['secret'])
token = xoauth.GenerateXOauthString(
    consumer, access, config['email'], 'imap', config['email'], nonce, timestamp)

# Connect to Gmail's IMAP service
imap = imaplib.IMAP4_SSL('imap.googlemail.com')
imap.debug = 4
imap.authenticate('XOAUTH', lambda x: token)

# Create the message
msg = email.message.Message()
msg['Subject'] = 'subject of the message'
msg['From'] = config['email']
msg['To'] = config['email']
msg.set_payload('Body of the message')

# Add the message to Gmail's drafts folder
now = imaplib.Time2Internaldate(time.time())
imap.append('[Gmail]/Drafts', '', now, str(msg))

imap.logout()
