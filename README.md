#Drafter

## What is Drafter?
Drafter programmatically generate Gmail drafts for you, complete with subject
lines, cc and bcc fields, and more.

## Drafter setup
Copy config.example.yaml to config.yaml.

###Create an OAuth token for Gmail
Use Google's [xoauth.py
module](https://code.google.com/p/google-mail-xoauth-tools/wiki/XoauthDotPyRunThrough)
(included) to generate tokens for accessing your account via OAuth:
```
python xoauth.py --generate_oauth_token --user=youremail@gmail.com
```
After following the steps the script provides, you'll get a URL to obtain a
verification code. Paste this code into the script and it will provide your
token and secret key. Include these in config.yaml, along with your email
address.

##Using Drafter
