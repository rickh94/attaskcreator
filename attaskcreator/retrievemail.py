# retrieve_mail.py - get and process email for gmailtoairtable
import email
# import email.utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import re
import smtplib
import os
from html2text import html2text
from nameparser import HumanName
# from attaskcreator import settings
import settings

class FetchMail():

    connection = None
    error = None

    def __init__(self, mail_server, username, password):
        self.connection = imaplib.IMAP4_SSL(mail_server)
        self.connection.login(username, password)
        self.connection.select('Inbox')

    def fetch_unread_messages(self):
        emails = []
        (result, messages) = self.connection.search(None, 'UnSeen')
        if result == 'OK':
            for message in messages[0].split():
                try:
                    ret, data = self.connection.fetch(message, '(RFC822)')
                except:
                    print("No new emails to read.")
                    self.close_connection()
                    exit()
                msg = email.message_from_bytes(data[0][1])
                if isinstance(msg, str) == False:
                    emails.append(msg)

            return emails

        self.error = "Failed to retreive emails."
        return emails

    def save_attachments(self, msg, download_folder="/tmp"):
        if not os.path.exists(download_folder):
            try:
                os.makedirs(download_folder)
            except PermissionError:
                download_folder = "/tmp"

        paths = []
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            att_path = os.path.join(download_folder, filename)

            if not os.path.isfile(att_path):
                fp = open(att_path, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()

            paths.append(att_path)

        return paths

    def read_info(self, msg):
        return {
                'from': msg['from'],
                'to': msg['to'],
                'subject': msg['subject'],
                'date': msg['date'],
                'body': html2text(self.get_text(msg)),
                }

    def get_text(self, mess):
        if mess.is_multipart():
            return self.get_text(mess.get_payload(0))
        else:
            return mess.get_payload(None, True).decode('utf-8')



"""
DEPRECATED (but keeping for a while for reference)
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
                        }
                mail_info.append(dict_of_data)

    # mail.close()
    return mail_info, mail

"""

def parse_to_field(email_to_field):
    # split name from email
    parsed = email.utils.parseaddr(email_to_field)
    # store email
    # parse name
    fname = ''
    lname = ''
    email_addr = parsed[1]
    if parsed[0] != '':
        name = HumanName(parsed[0])
        fname = name.first
        lname = name.last

    return { 
            'fname': fname,
            'lname': lname,
            'email': email_addr,
            }

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


