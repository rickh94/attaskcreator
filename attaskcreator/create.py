"""Main functions for attaskcreator."""
import argparse
import ast
import datetime
import logging
import re
from smtplib import SMTP
import socket

import daiquiri

from attaskcreator.config import Settings
from attaskcreator import retrievemail
from attaskcreator import s3interface
from attaskcreator import exceptions

LOGFILE = "/tmp/attest.log"


def choose_phrase(phrases, text):
    """Chooses the first phrase from a list of phrases that is found in the
    given text."""
    for phrase in phrases:
        if phrase.lower() in text.lower():
            return phrase
    # if a trigger phrase was not found, raise an exception.
    raise exceptions.NoPhraseError("Phrase was not found in {}.".format(text))


def parse_email_message(params, text_to_search):
    """Returns text found between a prefix and terminating character or None
    if it is not found.

    params: tuple of prefix phrase and terminating character(s).
    text_to_search: self-explanatory.
    """
    phrases, term_char = params
    # allow newline, etc. specification in config file
    # term_char = ast.literal_eval(term_char)
    # delete after term_char
    truncate = re.compile(r'^(.*){}'.format(term_char), re.DOTALL)
    search_text = truncate.search(text_to_search)
    try:
        trunc_text = search_text.group(1)
    except (AttributeError):
        raise exceptions.RegexFailedError(
            'Could not find {tc} in {st}'.format(tc=term_char,
                                                 st=text_to_search))
    # clean text_to_search
    text_oneline = trunc_text.replace('\n', ' ')
    text_clean = ' '.join(text_oneline.split())
    # will raise exception if nothing found, propogates to main.
    trigger_phrase = choose_phrase(phrases, text_clean)
    regex = re.compile(r'({} )(.*)'.format(re.escape(trigger_phrase)),
                       re.IGNORECASE
                       )
    found_text = regex.search(text_clean)
    try:
        return found_text.group(2)
    except AttributeError:
        raise exceptions.RegexFailedError(('Could not find text after {tp} in'
                                           ' {st}').format(
                                               tp=trigger_phrase,
                                               st=text_clean
                                           ))


def main():
    """Main function for attaskcreator."""
    # setup
    parser = argparse.ArgumentParser(
        prog='attaskcreator',
        description='Start attaskcreator email pull',
    )

    parser.add_argument('-p', '--config-prefix',
                        help=('Specify a folder where the configuration files'
                              ' are kept.')
                        )

    args = parser.parse_args()

    if args.config_prefix:
        settings = Settings(str(args.config_prefix))
    else:
        settings = Settings()

    settings.setup_log()
    logger = daiquiri.getLogger(__name__)

    try:
        settings.setup_all()
    except exceptions.ConfigError:
        logging.exception("The configuration files are not valid. Details:")
        raise SystemExit(1)

    try:
        mail = retrievemail.FetchMail(settings.eml_imap_server)
        messages = mail.fetch_unread_messages(settings.eml_username,
                                              settings.eml_pwd)
    except exceptions.EmailError:
        logging.exception("There was a problem retrieving email: ")
        raise SystemExit(1)

    atdb = settings.database

    # loop through email messages
    for mess in messages:
        data = retrievemail.read_msg_info(mess)
        try:
            parsed_text = parse_email_message(
                (settings.trigger_phrases, settings.term_char), data['body']
                )
            # get needed info
            to_info = retrievemail.parse_to_field(data['to'])
            people = []
            for person in to_info:
                person_id = atdb.search_for_email(
                    settings.at_people_table,
                    (settings.people_table_key, person['email']),
                    ("First Name", person['fname']),
                    ("Last Name", person['lname'])
                    )
                people.append(person_id)

            # save any attachments
            attachments = retrievemail.save_attachments(mess,
                                                        "/tmp/attach_down")

            # if there are attachments, upload them to s3 and send urls to
            # airtable.
            file_info = ()
            if attachments:
                try:
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
                except exceptions.NoAttachmentError:
                    file_info = ()

            notes_info = ()
            if settings.tasks_table_notes is not None:
                notes_info = (settings.tasks_table_notes, data['body'])

            logger.info('sender info is {}'.format(data['from']))
            logger.info('add info is {}'.format(data))
            # pass to record method for creation
            atdb.create_task_record(
                settings.at_tasks_table,
                (settings.tasks_table_text, parsed_text),
                (settings.tasks_table_person, people),
                notes_info,
                file_info,
                sender_filter=settings.sender_filter,
                sender_info=data['from'],
                )
        except (exceptions.RegexFailedError, exceptions.NoPhraseError):
            logger.exception("No record was created.")
            subject = 'Failed to create airtable task record'
            body = ('The trigger phrase was not found in your email to '
                    + data['to']
                    + ', so a record was not created. The body of the email'
                    + 'is below:\n\n'
                    + 'Subject: {}\n'.format(data['subject'])
                    + data['body']
                    )
            try:
                retrievemail.sendmsg(
                    SMTP(settings.eml_smtp_server, 587),
                    (settings.eml_username, settings.eml_pwd),
                    ('Airtable Task Creator', settings.eml_username),
                    ('User', settings.eml_error),
                    (subject, body)
                    )
            except socket.gaierror:
                logging.exception("Problem creating smtp connection: ")
            except exceptions.EmailError:
                logging.exception("Problem sending failure email: ")


if __name__ == "__main__":
    main()
