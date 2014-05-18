# Flashback - python script for emailing images from the past

Looks up images from Google Drive taken on the current day but in the past and sends those via email.

## Setup

pip install --upgrade google-api-python-client
pip install --upgrade boto

Create a config.cfg file with the following content:

```
[default]
aws_access_key_id=YOUR_AWS_ACCESS_KEY
aws_access_key_secret=YOUR_AWS_SECRET_KEY
```

First time the script is run it will guide you through the Google Drive OAuth dance.

## Running

```
python flashback.py sender@example.com recepient1@example.com recepient2@example.com
```
