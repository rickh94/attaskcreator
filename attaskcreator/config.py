# config.py - get global settings for gmailtoairtable
import configparser
from attaskcreator import settings
from airtable import airtable
DEBUG = 0

# idomatic attribute setting 
def setattrs(_self, **kwargs):
    for k,v in kwargs.items():
        setattr(_self, k, v)

def get_settings():
    config = configparser.ConfigParser()
    # development location for file
    if DEBUG == 1:
        config.read("../login.conf")
    else:
        config.read("/etc/attaskcreator/attaskcreator.conf")

    # make airtable object
    at = airtable.Airtable(
            config['Airtable']['database id'],
            config['Airtable']['api key']
            )

    setattrs(settings, 
            eml_username = config['Email']['user'],
            eml_pwd = config['Email']['password'],
            eml_imap_server = config['Email']['imap url'],
            eml_smtp_server = config['Email']['smtp url'],
            eml_error = config['Email']['error email'],

            database = at,

            at_tasks_table = config['Tasks Table']['name'],
            tasks_table_link = config['Tasks Table']['link field'],
            tasks_table_text = config['Tasks Table']['text field'],
            tasks_table_notes = config.get('Tasks Table', 'notes field', \
                fallback=None),

            at_people_table = config['People Table']['name'],
            people_table_key = config['People Table']['email field'],

            trigger_phrase = config['Parse']['trigger phrase'],
            term_char = config['Parse']['termination character']
            )
    
