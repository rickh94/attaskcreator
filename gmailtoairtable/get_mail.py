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
    setattr(settings, 'eml_smtp_server', config['email']['imap url'])

    # set airtable settings
    at = airtable.Airtable(
            config['airtable']['database id'],
            config['airtable']['api key']
            )
    setattr(settings, 'database', at)
    setattr(settings, 'at_insert_table', \
            config['airtable']['insert table'])
    setattr(settings, 'at_link_table', \
            config['airtable']['link table'])
    setattr(settings, 'link_field', config['airtable']['link field'])
    setattr(settings, 'trigger_phrase', config['parse']['Trigger Phrase'])
    setattr(settings, 'term_char', config['parse']['Termination Character'])
    

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
                dict_of_data['number'] = num
                mail_info.append(dict_of_data)

        # mail.store(num, '+FLAGS', '\Seen')

    # mail.close()
    return mail_info, mail

def search_for_email(email_addr, fname, lname):
    # get data
    at = settings.database
    table_name = settings.at_link_table
    table = at.get(table_name)
    # search for existing data
    search_field = settings.link_field
    curr_id = '' # for keeping track of the current record id
    # print(table_name)
    for rec in table['records']:
        for k, v in rec.items():
            curr_id = rec['id']
            if email_addr in rec['fields'][search_field]:
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

def parse_email_message(text_to_search):
    trigger_phrase = re.escape(settings.trigger_phrase)
    term_char = re.escape(settings.term_char)
    regex = re.compile(r'({} )([^{}]*)'.format(trigger_phrase, term_char),
            re.IGNORECASE
            )
    found_text = regex.search(text_to_search)
    try:
        return found_text.group(2)
    except AttributeError:
        return None



def main():
    get_settings()
    email_info, email_obj = readmail()
    # debugging code
    # print(email)
    # for mess in email_info:
    #     for k, v in mess.items():
    #         print(k, ':', v)
    # print(search_for_email("testemail@test.tech", "test", "person"))

    # get record id for 
    for mess in email_info:
        # debugging code
        # print(email['to'])
        to_info = parse_to_field(mess['to'])
        rec_id = search_for_email(to_info['email'], to_info['fname'], \
                to_info['lname'])
        # email_obj.store(mess['number'], '+FLAGS', '\Seen')
        parsed_text = parse_email_message(mess['body'])
        if parsed_text:
            print(parsed_text)
        else:
            print("No text")
        
        # debugging code
        # pprint(to_info)
        # print(rec_id)

    # debugging code
    # parsed_text = parse_email_message('this will fail')
    # parsed_text = parse_email_message('Can you please print this out?')
    # if parsed_text:
    #     print(parsed_text)
    # else:
    #     print("No text")
    # pprint(some_email)
    email_obj.close()


if __name__ == "__main__":
    main()
