---
# Example email message template for Drafter
# Message templates can optionally include YAML front matter that specifies
# from, to, cc, bcc, and subject fields. The message itself is written in
# Markdown, and Mustache variables can be mixed in anywhere.
from: george.bluth.sr@bluthcompany.com
to: "{{recipient}}"
#cc: <not included in this email example, but possible>
bcc: michael.bluth@bluthcompany.com
subject: "{{first_name}}, there's always money in the banana stand!"
---
Hey {{first_name}} {{last_name}},

I thought I'd tell you this first since you're my favorite
{{relationship}}. Just remember-- there's always money in the banana stand! ;)
(if you've forgotten where it is, [here's a link to it on Google
Maps](https://maps.google.com/maps?q=fisherman's+village+marina+del+rey&aq=f&um=1&ie=UTF-8&hl=en&sa=N&tab=wl&authuser=0)).


Just test!

\- George Bluth Sr.
