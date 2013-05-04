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
