# config.py - get global settings for gmailtoairtable
import configparser
import atexit, os
# from attaskcreator import settings
import settings
from airtable import airtable
DEBUG = 1

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
            # email config
            eml_username = config['Email']['user'],
            eml_pwd = config['Email']['password'],
            eml_imap_server = config['Email']['imap url'],
            eml_smtp_server = config['Email']['smtp url'],
            eml_error = config['Email']['error email'],

            # database config
            database = at,

            # temporary bucket
            bucket = config['AWS']['bucket'],

            # tasks table
            at_tasks_table = config['Tasks Table']['name'],
            tasks_table_person = config['Tasks Table']['people link field'],
            tasks_table_text = config['Tasks Table']['text field'],
            tasks_table_notes = config.get('Tasks Table', 'notes field', \
                fallback=None),
            tasks_table_attach = config['Tasks Table']['attachment link field'],

            # people table
            at_people_table = config['People Table']['name'],
            people_table_key = config['People Table']['email field'],

            # files table
            at_files_table = config['Files Table']['name'],
            files_table_name_field = config['Files Table']['key field'],
            files_table_attach_field = \
                    config['Files Table']['Attachment Field'],

            # text parsing config
            trigger_phrase = config['Parse']['trigger phrase'],
            term_char = config['Parse']['termination character'],
            )

    # set environment variables for aws
    os.environ['AWS_ACCESS_KEY_ID'] = config['AWS']['access key id']
    os.environ['AWS_SECRET_ACCESS_KEY'] = config['AWS']['secret access key']

    # just in case, to prevent credential security issues
    atexit.register(unset_aws)

def unset_aws():
    os.environ['AWS_ACCESS_KEY_ID'] = ''
    os.environ['AWS_SECRET_ACCESS_KEY'] = ''
    
