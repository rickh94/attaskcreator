"""Configure attaskcreator."""
import configparser
import atexit
import os
import logging
import daiquiri
from attaskcreator import settings
from attaskcreator.atinterface import MyDatabase
from attaskcreator import exceptions


class Settings(object):
    """Sets the various configuration options for attaskcreator."""
    def __init__(self, path_prefix="/etc/attaskcreator"):
        """Read the configuration files."""
        self.login = configparser.ConfigParser()
        self.tables = configparser.ConfigParser()
        try:
            self.login.read(os.path.join(path_prefix, 'login'))
            self.tables.read(os.path.join(path_prefix, 'tables'))
            with open(os.path.join(path_prefix, 'phrases'), "r") as f:
                self.trigger_phrases = f.readlines()
        except OSError:
            logging.exception(
                'Could not open config files. Traceback Follows:')
            raise SystemExit(1)
        self.logger = daiquiri.getLogger(__name__)

    def setup_eml(self):
        """Sets email options."""
        try:
            self.eml_username = self.login['Email']['user']
            self.eml_pwd = self.login['Email']['password']
            self.eml_imap_server = self.login['Email']['imap url']
            self.eml_smtp_server = self.login['Email']['smtp url']
            self.eml_error = self.login['Email']['error email']
        except KeyError as err:
            raise exceptions.ConfigError(
                'Missing email config info: {}'.format(err))

    def setup_db(self):
        """Sets up the airtable database."""
        if 'app' not in self.login['Airtable']['database id']:
            raise exceptions.ConfigError("Database ID is not correct")
        if 'key' not in self.login['Airtable']['api key']:
            raise exceptions.ConfigError("API key is not correct")
        try:
            self.database = MyDatabase(
                self.login['Airtable']['database id'],
                self.login['Airtable']['api key']
            )
        except KeyError as err:
            raise exceptions.ConfigError(
                'Missing airtable config info: {}'.format(err))

    def setup_phrases(self):
        """Sets up the trigger phrases and termination character for
        attaskcreator.
        """
        self.phrases = list(map(lambda x: x.strip(), self.phrases))
        self.term_char = self.tables['Parse']['termination character']

    def setup_aws(self):
        """Sets up AWS access info and bucket. If running hosted in AWS this
        should be implemented using IAM and NOT an API key.
        """
        try:
            os.environ['AWS_ACCESS_KEY_ID'] = (
                self.login['AWS']['access key id'])
            os.environ['AWS_SECRET_ACCESS_KEY'] = (
                self.login['AWS']['secret access key'])
        except KeyError:
            error = exceptions.ConfigError("AWS access configuration missing")
            try:
                if self.login['AWS']['using iam'].lower() == 'true':
                    pass
                else:
                    raise error
            except KeyError:
                raise error
        else:
            atexit.register(unset_aws)
        try:
            self.bucket = self.login['AWS']['bucket']
        except KeyError:
            raise exceptions.ConfigError("AWS bucket configuration missing.")

    def setup_tables(self):
        """Setup the tables for record search and insertion in airtable."""
        try:
            # tasks table
            self.at_tasks_table = self.tables['Tasks Table']['name']
            self.tasks_table_person = (
                self.tables['Tasks Table']['people link field'])
            self.tasks_table_text = self.tables['Tasks Table']['text field']
            self.tasks_table_attach = (
                self.tables['Tasks Table']['attachment link field'])

            # people table
            self.at_people_table = self.tables['People Table']['name']
            self.people_table_key = self.tables['People Table']['email field']

            # files table
            self.at_files_table = self.tables['Files Table']['name']
            self.files_table_name_field = (
                self.tables['Files Table']['key field'])
            self.files_table_attach_field = (
                 self.tables['Files Table']['Attachment Field'])
        except KeyError as err:
            raise exceptions.ConfigError(
                "Table configuration missing: {}".format(err))
        try:
            self.tasks_table_notes = self.tables['Tasks Table']['notes field']
        except KeyError:
            pass

    def setup_log(self):
        try:
            logfile = self.login['Logging']['File']
        except KeyError:
            logfile = '/tmp/attaskcreator.log'
        daiquiri.setup(level=logging.INFO, outputs=(
            daiquiri.output.File(logfile),
        ))

    def setup_all(self):
        """Sets up everything for attaskcreator.  """
        self.setup_eml()
        self.setup_db()
        self.setup_phrases()
        self.setup_aws()
        self.setup_tables()


def unset_aws():
    """Unset AWS environment variables to prevent security issues."""
    os.environ['AWS_ACCESS_KEY_ID'] = ''
    os.environ['AWS_SECRET_ACCESS_KEY'] = ''
