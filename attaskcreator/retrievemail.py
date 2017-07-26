# retrieve_mail.py - get and process email for gmailtoairtable
import email
# import email.utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import re
import smtplib
import os
import imaplib
import datetime
from html2text import html2text
from nameparser import HumanName
from attaskcreator import settings


class FetchMail(imaplib.IMAP4_SSL):
    """Class for getting email and associated methods."""

    def select_inbox(self, username, password):
        """Select email from Inbox."""
        self.login(username, password)
        self.select('Inbox')

    def fetch_unread_messages(self, username, password):
        """Gets unread messages from Inbox."""
        self.select_inbox(username, password)
        emails = []
        result, messages = self.search(None, 'UnSeen')
        if result == 'OK':
            for message in messages[0].split():
                try:
                    _, data = self.fetch(message, '(RFC822)')
                except Exception:
                    print("No new emails to read.")
                    self.close()
                    exit()
                msg = email.message_from_bytes(data[0][1])
                if not isinstance(msg, str):
                    emails.append(msg)

            return emails

        return emails


def save_attachments(msg, download_dir="/tmp"):
    """Save attachments out of an email message to a given folder and return
    list of paths to downloaded files.

    Optionally a download directory can be specified and will be created if it
    does not already exist. If it cannot be written to, /tmp will be used
    instead. The date/time at runtime will be appended to the filename to
    prevent accidental overwriting.
    """
    if not os.path.exists(download_dir):
        try:
            os.makedirs(download_dir)
        except PermissionError:
            download_folder = "/tmp"

    paths = []
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue

        # adds current time to the file to prevent accidental overwriting of files
        filename = part.get_filename() + 'T' + str(datetime.datetime.today())
        att_path = os.path.join(download_folder, filename)
        with open(att_path, 'wb') as thisfile:
            thisfile.write(part.get_payload(decode=True))

        paths.append(att_path)

    return paths

def read_msg_info(msg):
    """Reads/decodes the message info needed for attaskcreator and returns it
    as a dict."""
    return {
        'from': msg['from'],
        'to': msg['to'],
        'subject': msg['subject'],
        'date': msg['date'],
        'body': html2text(get_msg_text(msg)),
    }

def get_msg_text(mess):
    """Finds the text body of a message and returns it."""
    if mess.is_multipart():
        return get_msg_text(mess.get_payload(0))
    else:
        return mess.get_payload(None, True).decode('utf-8')

def parse_to_field(email_to_field):
    """Splits to field of an email to firstname, lastname, and email address
    components and returns as a dict."""
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

def sendmsg(smtp_server, login_info, from_info, to_info, message):
    """This basically wraps smtplib.SMTP.sendmail to configure a few options
    more cleanly.

    smtp_server is a tuple of the url and port for an smtp server
    login_info is a tuple of a matching username and password
    from_info and to_info are tuples of a name and email address to send from
    and to.
    message is a tuple of subject and body text.
    """
    from_eml = email.utils.formataddr(from_info)
    to_eml = email.utils.formataddr(to_info)
    url, port = smtp_server
    eml, pwd = login_info
    subject, body = message

    # login to server
    server = smtplib.SMTP(url, port)
    server.starttls()
    server.login(eml, pwd)

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
