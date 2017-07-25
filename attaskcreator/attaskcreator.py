#!/usr/bin/env python3

import json
import re
from attaskcreator import settings
from attaskcreator.config import setattrs
from attaskcreator.config import get_settings
from attaskcreator import retrievemail
from attaskcreator import atinterface
from attaskcreator import s3interface

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
    mail = retrievemail.FetchMail(
            settings.eml_imap_server, 
            settings.eml_username,
            settings.eml_pwd
            )
    messages = mail.fetch_unread_messages()

    # loop through email messages
    for mess in messages:
        data = mail.read_info(mess)
        parsed_text = parse_email_message(data['body'])
        if parsed_text:
            # get needed info
            to_info = retrievemail.parse_to_field(data['to'])
            found_rec_id = atinterface.search_for_email(
                    to_info['email'],
                    to_info['fname'],
                    to_info['lname']
                    )
            # save any attachments
            attachments = mail.save_attachments(mess, "/tmp/attach_down")

            # if there are attachments, upload them to s3 and send urls to
            # airtable.
            file_rec = None
            if attachments != []:
                s3_urls = []
                for path in attachments:
                    url = s3interface.make_url(path, settings.bucket)
                    s3_urls.append(url)
                file_rec = atinterface.at_upload_attach(parsed_text, s3_urls)

            # pass to record method for creation
            atinterface.create_task_record(
                    parsed_text, 
                    found_rec_id,
                    mess['body'],
                    file_rec
                    )
        else:
            subject = 'Failed to create airtable task record'
            body = 'The trigger phrase was not found in your email to ' + \
                    mess['to'] + \
                    ', so a record was not created. The body of the email '+ \
                    'is below:\n\n' + \
                    'Subject: {}'.format(mess['subject']) +\
                    '\n' + mess['body']
            retrievemail.sendmsg(subject, body)


if __name__ == "__main__":
    main()
