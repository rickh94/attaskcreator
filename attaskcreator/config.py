"""Configure attaskcreator."""
import configparser
import atexit
import os
from attaskcreator import settings
from attaskcreator.atinterface import MyDatabase

# idomatic attribute setting


def setattrs(_self, **kwargs):
    """Quickly set multiple attributes from key value pairs)."""
    for k, v in kwargs.items():
        setattr(_self, k, v)


def get_settings():
    """Reads /etc/attaskcreator/attaskcreator.conf to configure needed options.

    Login options are stored, used to login, or exported to the environment.
    """
    login = configparser.ConfigParser()
    login.read("/etc/attaskcreator/login.conf")
    tables = configparser.ConfigParser()
    tables.read("/etc/attaskcreator/tables.conf")
    with open("/etc/attaskcreator/phrases.conf", "r") as f:
        phrases = f.readlines()

    # strip whitespace and newlines
    phrases = list(map(lambda x: x.strip(), phrases))

    # make airtable object
    atdb = MyDatabase(
        login['Airtable']['database id'],
        login['Airtable']['api key']
    )

    setattrs(settings,
             # email config
             eml_username=login['Email']['user'],
             eml_pwd=login['Email']['password'],
             eml_imap_server=login['Email']['imap url'],
             eml_smtp_server=login['Email']['smtp url'],
             eml_error=login['Email']['error email'],

             # database config
             database=atdb,

             # temporary bucket
             bucket=login['AWS']['bucket'],

             # tasks table
             at_tasks_table=tables['Tasks Table']['name'],
             tasks_table_person=tables['Tasks Table']['people link field'],
             tasks_table_text=tables['Tasks Table']['text field'],
             tasks_table_notes=tables['Tasks Table']['notes field'],
             tasks_table_attach=tables['Tasks Table']['attachment link field'],

             # people table
             at_people_table=tables['People Table']['name'],
             people_table_key=tables['People Table']['email field'],

             # files table
             at_files_table=tables['Files Table']['name'],
             files_table_name_field=tables['Files Table']['key field'],
             files_table_attach_field=tables['Files Table']['Attachment Field'],

             # text parsing config
             trigger_phrases=phrases,
             term_char=tables['Parse']['termination character'],
            )

    # set environment variables for aws
    os.environ['AWS_ACCESS_KEY_ID'] = login['AWS']['access key id']
    os.environ['AWS_SECRET_ACCESS_KEY'] = login['AWS']['secret access key']

    atexit.register(unset_aws)


def unset_aws():
    """Unset AWS environment variables to prevent security issues."""
    os.environ['AWS_ACCESS_KEY_ID'] = ''
    os.environ['AWS_SECRET_ACCESS_KEY'] = ''
