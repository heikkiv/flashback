# coding=utf-8

# Based on https://gist.github.com/yosemitebandit/2883593
# and http://code.activestate.com/recipes/473810-send-an-html-email-with-embedded-image-and-plain-t/

from email.mime.text import MIMEText
from email.MIMEImage import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.header import Header

import boto


def send_email(today, source, recipients, subject, dates_and_filenames, id_and_secret):
    msg = MIMEMultipart()
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = source
    msg['To'] = ', '.join(recipients)

    # what a recipient sees if they don't use an email reader
    msg.preamble = 'This is a multi-part message in MIME format.\n'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msg_alternative = MIMEMultipart('alternative')
    msg.attach(msg_alternative)

    msg_text = MIMEText('This is the alternative plain text message.')
    msg_alternative.attach(msg_text)

    # the pictures
    html = u'<h3>Tapahtui tänään %d.%d. edellisinä vuosina</h3>' % (today[2], today[1])
    for date, filename in dates_and_filenames:

        html += u'<strong>%d.%d.%d</strong>' % (date[2], date[1], date[0])
        html += u'<br><br><img src="cid:' + filename + u'">'

         # This example assumes the image is in the current directory
        fp = open(filename, 'rb')
        msg_image = MIMEImage(fp.read())
        fp.close()

        # Define the image's ID as referenced above
        msg_image.add_header('Content-ID', '<' + filename + '>')
        msg.attach(msg_image)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    msg_text = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
    msg_alternative.attach(msg_text)

    # connect to SES
    connection = boto.connect_ses(aws_access_key_id=id_and_secret[0]
                                  , aws_secret_access_key=id_and_secret[1])

    # and send the message
    result = connection.send_raw_email(msg.as_string()
                                       , source=msg['From']
                                       , destinations=[msg['To']])
    return result
