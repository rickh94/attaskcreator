#!/usr/bin/env python3

# change a few settings based on development vs production
DEBUG = 0

import json
import re

if DEBUG == 1:
    import settings
    from config import get_settings
    from config import setattrs
    from pprint import pprint
    import retrieve_mail
    import at_interface
else:
    from attaskcreator import settings
    from attaskcreator.config import setattrs
    from attaskcreator.config import get_settings
    from attaskcreator import retrieve_mail
    from attaskcreator import at_interface

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
    # get settings and email
    get_settings()
    mail = retrieve_mail.FetchMail(
            settings.eml_imap_server, 
            eml_username,
            eml_pwd
            )
    messages = mail.fetch_unread_messages()
    email_data = []
    for mess in messages:
        email_data.append(mail.read_info(mess))


    # loop through email messages
    for mess in email_info:
        parsed_text = parse_email_message(mess['body'])
        if parsed_text:
            to_info = retrieve_mail.parse_to_field(mess['to'])
            found_rec_id = at_interface.search_for_email(
                    to_info['email'],
                    to_info['fname'],
                    to_info['lname']
                    )
            at_interface.create_task_record(
                    parsed_text, 
                    found_rec_id,
                    mess['body']
                    )
        else:
            subject = 'Failed to create airtable task record'
            body = 'The trigger phrase was not found in your email to ' + \
                    mess['to'] + \
                    ', so a record was not created. The body of the email '+ \
                    'is below:\n\n' + \
                    'Subject: {}'.format(mess['subject']) +\
                    '\n' + mess['body']
            retrieve_mail.sendmsg(subject, body)
            # retrieve_mail.markunread(email_obj, mess['number'])
                    
    retrieve_mail.closemail(email_obj)


if __name__ == "__main__":
    main()
