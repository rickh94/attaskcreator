# at_interface.py - all the airtable calls for gmailtoairtable
from airtable import airtable
# from attaskcreator import settings
import settings

# find email in link table


def search_for_email(email_addr, fname, lname):
    # get data
    at = settings.database
    table_name = settings.at_people_table
    # search for existing data
    search_field = settings.people_table_key
    curr_id = ''  # for keeping track of the current record id
    # print(table_name)
    rec_id = search_for_rec(table_name, search_field, email_addr)
    if rec_id is not None:
        return rec_id
    else:
        # create new record if none found
        data = {
            "Email": email_addr,
            "First Name": fname,
            "Last Name": lname,
        }

        at.create(table_name, data)

        # recursive call to return record id for created record
        return search_for_rec(table_name, search_field, email_addr)


def search_for_rec(table, field, term):
    curr_id = ''
    at = settings.database
    table = at.get(table)
    for rec in table['records']:
        for k, v in rec.items():
            curr_id = rec['id']
            try:
                if term in rec['fields'][field]:
                    # return if search term is found
                    return(curr_id)
            # if key is missing entirely, skip to next record
            except KeyError:
                continue

    # return none if nothing found (for control flow)
    return None


def create_task_record(text, rec_id, email_body, attach_rec=None):
    # needed info, easier to access
    at = settings.database
    table_name = settings.at_tasks_table
    text_field = settings.tasks_table_text
    link_field = settings.tasks_table_person
    notes_field = settings.tasks_table_notes
    attach_field = settings.tasks_table_attach

    # data for record
    data = {
        text_field: text,
        link_field: [rec_id],
    }
    # if a notes field was provided, put the email body into it

    if notes_field is not None:
        data[notes_field] = email_body

    if attach_rec is not None:
        data[attach_field] = [attach_rec]

    return at.create(table_name, data)


def at_upload_attach(rec_name, urls):
    # get settings
    at = settings.database
    table_name = settings.at_files_table
    name_field = settings.files_table_name_field
    attach_field = settings.files_table_attach_field

    all_urls = []

    for url in urls:
        all_urls.append({"url": url})

    data = {
        name_field: rec_name,
        attach_field: all_urls,
    }

    at.create(table_name, data)

    # return new rec id
    return search_for_rec(table_name, name_field, rec_name)
