#!/usr/bin/env python3

# change a few settings based on development vs production
DEBUG = 1

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
    from gmailtoairtable import settings
    from gmailtoairtable.config import setattrs
    from gmailtoairtable.config import get_settings
    from gmailtoairtable import retrieve_mail
    from gmailtoairtable import at_interface

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
    email_info, email_obj = retrieve_mail.readmail()

    # loop through email messages
    for mess in email_info:
        # debugging code
        # print(email['to'])
        # print(rec_id, to_info['email'])
        # email_obj.store(mess['number'], '+FLAGS', '\Seen')
        parsed_text = parse_email_message(mess['body'])
        if parsed_text:
            to_info = retrieve_mail.parse_to_field(mess['to'])
            found_rec_id = at_interface.search_for_email(
                    to_info['email'],
                    to_info['fname'],
                    to_info['lname']
                    )
            print(json.dumps(at_interface.create_task_record(
                    parsed_text, 
                    found_rec_id,
                    mess['body']
                    )))
            print('inserted a record')
        else:
            print('failed to create record')
        
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

    retrieve_mail.closemail(email_obj)


if __name__ == "__main__":
    main()
