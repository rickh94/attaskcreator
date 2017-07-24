# retrieve_mail.py - get and process email for gmailtoairtable
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import re
import smtplib
from html2text import html2text
from nameparser import HumanName
from attaskcreator import settings

def get_text(mess):
    if mess.is_multipart():
        return get_text(mess.get_payload(0))
    else:
        return mess.get_payload(None, True).decode('utf-8')

def readmail():
    mail_info = []
    mail = imaplib.IMAP4_SSL(settings.eml_imap_server)
    mail.login(settings.eml_username, settings.eml_pwd)
    mail.select('Inbox')

    typ, data = mail.search(None, 'UnSeen')

    for num in data[0].split():
        typ, data = mail.fetch(num, '(RFC822)')

        for response_part in data:
            dict_of_data = {}
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                # store headers in dict
                dict_of_data = {
                        'from': msg['from'],
                        'to': msg['to'],
                        'subject': msg['subject'],
                        'date': msg['date'],
                        'body': html2text(get_text(msg)),
                        'number': num,
                        }
                mail_info.append(dict_of_data)


    # mail.close()
    return mail_info, mail


def parse_to_field(email_to_field):
    # split name from email
    searched = re.search(r'([^<]*)<([^>]*)>', email_to_field)
    # store email
    # parse name
    try:
        email = searched.group(2)
        name = HumanName(searched.group(1))
        fname = name.first
        lname = name.last
    # return attributes
    except AttributeError:
        email = email_to_field
        fname = ''
        lname = ''
    return { 
            'fname': fname,
            'lname': lname,
            'email': email,
            }

def markread(eml, num):
    eml.store(num, '+FLAGS', '\Seen')

def markread(eml, num):
    eml.store(num, '+FLAGS', '\Seen')

def markunread(eml, num):
    eml.store(num, '-FLAGS', '\Seen')

def closemail(eml):
    eml.close()

def sendmsg(subject, body):
    from_eml = email.utils.formataddr(
            ("Airtable Task Creator", settings.eml_username)
            )
    to_eml = settings.eml_error

    # login to server
    server = smtplib.SMTP(settings.eml_smtp_server, 587)
    server.starttls()
    server.login(settings.eml_username, settings.eml_pwd)

    # assemble message
    msg = MIMEMultipart()
    msg['From'] = from_eml
    msg['To'] = to_eml
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))
    
    text = msg.as_string()

    # send the message
    server.sendmail(from_eml, to_eml, text)
    server.quit()


