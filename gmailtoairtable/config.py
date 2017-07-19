# config.py - get global settings for gmailtoairtable
import configparser
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
        config.read("/etc/gmailtoairtable/login.conf")

    # make airtable object
    at = airtable.Airtable(
            config['airtable']['database id'],
            config['airtable']['api key']
            )

    setattrs(settings, 
            eml_username = config['email']['user'],
            eml_pwd = config['email']['password'],
            eml_smtp_server = config['email']['imap url'],
            database = at,
            at_insert_table = config['airtable']['insert table'],
            at_link_table = config['airtable']['link table'],
            link_field = config['airtable']['link field'],
            trigger_phrase = config['parse']['Trigger Phrase'],
            term_char = config['parse']['Termination Character']
            )
    
