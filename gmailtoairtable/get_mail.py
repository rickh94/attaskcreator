#!/usr/bin/env python3

# change a few settings based on development vs production
DEBUG = 1

import smtplib, time, imaplib, email
import configparser
import json
import re
from nameparser import HumanName
from airtable import airtable
from io import BytesIO
from html2text import html2text

if DEBUG == 1:
    import settings
    from pprint import pprint
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
    at = airtable.Airtable(
            config['airtable']['database_id'],
            config['airtable']['api_key']
            )
    setattr(settings, 'database', at)
    setattr(settings, 'at_insert_table', \
            config['airtable']['insert_table_name'])
    setattr(settings, 'at_link_table', \
            config['airtable']['link_table_name'])
    setattr(settings, 'link_field', config['airtable']['link_field'])

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

def search_for_email(email_addr, fname, lname):
    # get data
    at = settings.database
    table_name = settings.at_link_table
    table = at.get(table_name)
    # search for existing data
    search_field = settings.link_field
    curr_id = '' # for keeping track of the current record id
    for rec in table['records']:
        for k, v in rec.items():
            if re.match('id', k, re.IGNORECASE):
                curr_id = v
            elif re.match('fields', k, re.IGNORECASE):
                for h, j in v.items():
                    if search_field in h and email_addr in j:
                        # debug code
                        # print(h, j)
                        return(curr_id)
    # create new record if none found
    data = { 
            "Email": email_addr,
            "First Name": fname,
            "Last Name": lname,
            }

    at.create(table_name, data)

    # recursive call to return record id for created record
    return search_for_email(email_addr, fname, lname)


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


def main():
    get_settings()
    some_email = readmail()
    # debugging code
    # for mess in some_email:
    #     for k, v in mess.items():
    #         print(k, ':', v)
    # print(search_for_email("testemail@test.tech", "test", "person"))
    for email in some_email:
        # print(email['to'])
        to_info = parse_to_field(email['to'])
        pprint(to_info)
        print(search_for_email(to_info['email'], to_info['fname'], \
                to_info['lname']))
        print('')

    # pprint(some_email)


if __name__ == "__main__":
    main()
