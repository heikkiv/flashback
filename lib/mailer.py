# From https://gist.github.com/yosemitebandit/2883593

from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

import boto


def send_email(text, filename, id_and_secret):
    # via http://codeadict.wordpress.com/2010/02/11/send-e-mails-with-attachment-in-python/
    msg = MIMEMultipart()
    msg['Subject'] = 'Flashback'
    msg['From'] = 'heikki.verta@gmail.com'
    msg['To'] = 'heikki.verta@gmail.com'

    # what a recipient sees if they don't use an email reader
    msg.preamble = 'Multipart message.\n'

    # the message body
    part = MIMEText(text)
    msg.attach(part)

    # the attachment
    part = MIMEApplication(open(filename, 'rb').read())
    part.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(part)

    # connect to SES
    connection = boto.connect_ses(aws_access_key_id=id_and_secret[0]
                                  , aws_secret_access_key=id_and_secret[1])

    # and send the message
    result = connection.send_raw_email(msg.as_string()
                                       , source=msg['From']
                                       , destinations=[msg['To']])
    print result
