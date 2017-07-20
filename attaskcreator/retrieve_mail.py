# mail_processing.py - get and process email for gmailtoairtable
import imaplib
import email
import time
import re
from html2text import html2text
from nameparser import HumanName
import settings

def get_text(mess):
    if mess.is_multipart():
        return get_text(mess.get_payload(0))
    else:
        return mess.get_payload(None, True).decode('utf-8')

def readmail():
    mail_info = []
    mail = imaplib.IMAP4_SSL(settings.eml_smtp_server)
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

        # mail.store(num, '+FLAGS', '\Seen')

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


def closemail(eml):
    eml.close()
