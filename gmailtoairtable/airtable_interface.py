# at_interface.py - all the airtable calls for gmailtoairtable
from airtable import airtable
import settings
import re

# find email in link table
def search_for_email(email_addr, fname, lname):
    # get data
    at = settings.database
    table_name = settings.at_link_table
    table = at.get(table_name)
    # search for existing data
    search_field = settings.link_field
    curr_id = '' # for keeping track of the current record id
    # print(table_name)
    eml_regex = re.compile('{}'.format(email_addr))
    for rec in table['records']:
        for k, v in rec.items():
            curr_id = rec['id']
            if eml_regex.match(rec['fields'][search_field]):
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
