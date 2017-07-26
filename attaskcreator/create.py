#!/usr/bin/env python3

import json
import re
import datetime
from attaskcreator import settings
from attaskcreator.config import setattrs
from attaskcreator.config import get_settings
from attaskcreator import retrievemail
# from attaskcreator import atinterface
from attaskcreator import s3interface

def parse_email_message(params, text_to_search):
    """Returns text found between a prefix and terminating character or None
    if it is not found.

    params: tuple of prefix phrase and terminating character.
    text_to_search: self-explanatory.
    """
    trigger_phrase, term_char = params
    regex = re.compile(r'({} )([^{}]*)'.format(trigger_phrase, term_char),
                       re.IGNORECASE
                      )
    found_text = regex.search(text_to_search)
    try:
        return found_text.group(2)
    except AttributeError:
        return None


def main():
    """Main function for attaskcreator."""
    # get settings and email
    get_settings()
    mail = retrievemail.FetchMail(
        settings.eml_imap_server
        )
    messages = mail.fetch_unread_messages(settings.eml_username,
                                          settings.eml_pwd)
    atdb = settings.database

    # loop through email messages
    for mess in messages:
        data = retrievemail.read_msg_info(mess)

        parsed_text = parse_email_message(
            (settings.trigger_phrase, settings.term_char), data['body']
            )
        if parsed_text:
            # get needed info
            to_info = retrievemail.parse_to_field(data['to'])
            person_id = atdb.search_for_email(
                settings.at_people_table,
                (settings.people_table_key, to_info['email']),
                ("First Name", to_info['fname']),
                ("Last Name", to_info['lname'])
                )
            # save any attachments
            attachments = retrievemail.save_attachments(mess, "/tmp/attach_down")

            # if there are attachments, upload them to s3 and send urls to
            # airtable.
            file_info = ()
            if attachments:
                s3_urls = []
                for path in attachments:
                    url = s3interface.make_url(path, settings.bucket)
                    s3_urls.append(url)
                # tag text with date to prevent duplicate records
                tagged_text = ' T:'.join(
                    (parsed_text, str(datetime.datetime.today()))
                    )
                file_rec = atdb.upload_attach(
                    settings.at_files_table,
                    (settings.files_table_name_field, tagged_text),
                    (settings.files_table_attach_field, s3_urls)
                    )
                file_info = (settings.tasks_table_attach, file_rec)


            notes_info = ()
            if settings.tasks_table_notes is not None:
                notes_info = (settings.tasks_table_notes, data['body'])


            # pass to record method for creation
            atdb.create_task_record(
                settings.at_tasks_table,
                (settings.tasks_table_text, parsed_text),
                (settings.tasks_table_person, person_id),
                notes_info,
                file_info
                )
        else:
            subject = 'Failed to create airtable task record'
            body = ('The trigger phrase was not found in your email to'
                    + mess['to']
                    + ', so a record was not created. The body of the email'
                    + 'is below:\n\n'
                    + 'Subject: {}\n'.format(mess['subject'])
                    + mess['body']
                   )
            retrievemail.sendmsg(
                (settings.eml_smtp_server, 587),
                (settings.eml_username, settings.eml_pwd),
                ('Airtable Task Creator', settings.eml_username),
                ('User', settings.eml_error),
                (subject, body)
                )


if __name__ == "__main__":
    main()
