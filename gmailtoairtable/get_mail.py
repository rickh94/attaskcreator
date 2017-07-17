#!/usr/bin/env python3

# change a few settings based on development vs production
DEBUG = 1

import smtplib, time, imaplib, email
import configparser
import subprocess
import sys
import pycurl
import json
from io import BytesIO
from html2text import html2text

if DEBUG == 1:
    import settings
else:
    from gmailtoairtable import settings


# class EmailINeed():
    # def __init__(headers, content):

def get_settings():
    config = configparser.ConfigParser()
    # development location for file
    if DEBUG == 1:
        config.read("../login.conf")
    else:
        config.read("/etc/gmailtoairtable/login.conf")

    # set email settings
    setattr(settings, 'eml_username', config['email']['user'])
    setattr(settings, 'eml_pwd', config['email']['password'])
    setattr(settings, 'eml_smtp_server', config['email']['imap_url'])

    # set airtable settings
    setattr(settings, 'at_api_key', config['airtable']['api_key'])
    setattr(settings, 'at_database_id', config['airtable']['database_id'])
    setattr(settings, 'at_insert_table', \
            config['airtable']['insert_table_name'].replace(' ', '%20'))
    setattr(settings, 'at_link_table', \
            config['airtable']['link_table_name'].replace(' ', '%20'))


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
                dict_of_data['from'] = msg['from']
                dict_of_data['to'] = msg['to']
                dict_of_data['subject'] = msg['subject']
                dict_of_data['date'] = msg['date']
                dict_of_data['body'] = html2text(get_text(msg))
                mail_info.append(dict_of_data)

        mail.store(num, '+FLAGS', '\Seen')

    mail.close()
    return mail_info

# generate curl calls to airtable
def at_curl(action, table,):
    # needed info for easy access
    at_base_url = "https://api.airtable.com/v0/"
    at_db = settings.at_database_id
    at_api_key = settings.at_api_key
    at_auth_cmd = "Authorization: Bearer " + at_api_key 
    at_headers = [at_auth_cmd]

    full_command = ['curl']
    # set the correct table
    if 'link' in table:
        table = settings.at_link_table
    elif 'insert' in table:
        table = settings.at_insert_table
    else:
        print('No matching table found. Curl failed')
        sys.exit(1)

    buffer = BytesIO()
    cmd = pycurl.Curl()
    if 'get' in action:
        full_url = at_base_url + at_db + "/" + table 

    cmd.setopt(cmd.URL, full_url)
    cmd.setopt(cmd.HTTPHEADER, at_headers)
    cmd.setopt(cmd.WRITEDATA, buffer)
    cmd.perform()
    cmd.close()
    stuff = buffer.getvalue()
    #
    return stuff.decode('utf-8')

    

def main():
    get_settings()
    some_email = readmail()
    # debugging code
    for mess in some_email:
        for k, v in mess.items():
            print(k, ':', v)
    data = at_curl('get', 'insert')
    parsed = json.loads(data)
    print(json.dumps(parsed, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
