# at_interface.py - all the airtable calls for gmailtoairtable
from airtable import airtable
from attaskcreator import settings

# find email in link table
def search_for_email(email_addr, fname, lname):
    # get data
    at = settings.database
    table_name = settings.at_people_table
    table = at.get(table_name)
    # search for existing data
    search_field = settings.people_table_key
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

def create_task_record(text, rec_id, email_body):
    # needed info, easier to access
    at = settings.database
    table_name = settings.at_tasks_table
    text_field = settings.tasks_table_text
    link_field = settings.tasks_table_link
    notes_field = settings.tasks_table_notes

    # data for record
    data = {
            text_field: text,
            link_field: [rec_id],
            }
    # if a notes field was provided, put the email body into it

    if notes_field:
        data[notes_field] = email_body


    return at.create(table_name, data)

def at_upload_attach(rec_name, *urls):
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


