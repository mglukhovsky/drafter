# Drafter

Drafter does command-line mail merge-- it programmatically generates Gmail
drafts for you, complete with subject
lines, cc and bcc fields, and more.

Drafter __does not__ automatically send email for
you. It generates drafts for you in Gmail, allowing you to review and approve
each email before you send it out.

Drafter builds HTML and plain-text email based on simple Mustache templates and
are written in Markdown. Fields like the subject line, cc, and bcc are specified using
YAML (and Mustache tags can be used anywhere).

Here's an example of a simple email template:
```
---
to: {{recipient}}
subject: {{first_name}}, come to my birthday party this weekend!
---
Hey {{firstname}}, just a heads up, my birthday is coming up and I'd love for
you to be there. Make sure to bring {{significant_other}}!
- Joe
```

To generate Gmail drafts, create a CSV file with the headers `recipient`,
`first_name` and `significant_other` and all the contacts you'd like to email,
and just run:
```
python drafter.py --template /path/to/template.markdown --csv-data /path/to/data.csv
```

Drafter will then log in to your Gmail accout and create a set of drafts based
on your template and CSV data.

## Drafter setup
Start by installing the required libraries:
```
pip install -r requirements.txt
```

Then set up some configuration details for Drafter by copying
config.example.yaml to config.yaml:
```
cp config.example.yaml config.yaml
```

Edit the configuration to include your Gmail OAuth token and login details.

### Creating an OAuth token for Gmail
Before you can use Drafter, you have to generate a personal API key for Gmail.

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
