"""This module performs the interaction with airtable for attaskcreator.

Contains functions for searching for records, creating records, and uploading
files from urls.
"""
import logging
from airtable.airtable import Airtable
import daiquiri
from attaskcreator import exceptions

LOGGER = daiquiri.getLogger(__name__)


class MyDatabase(Airtable):
    """This class extends the Airtable class for specific uses.

    It has additonal searching methods and the ability to upload files more
    easily.
    """

    def search_for_rec(self, table, field, term):
        """Searches for a record in an airtable database table and returns its
        'id' if found and None if it is not found.

        The search is performed in a specified field for a specified term.
        """
        try:
            table = self.get(table)
        except AttributeError:
            logging.exception(("Could not get table. Check database id "
                               "API key and table name. Traceback follows:"))
            raise SystemExit(1)
        found = False
        for rec in table['records']:
            curr_id = rec['id']
            try:
                if term.lower() in rec['fields'][field].lower():
                    # return if search term is found
                    found = True
                    return curr_id
            # deal with json's lack of normalization
            except KeyError:
                continue

        if not found:
            raise exceptions.NoRecordError

    def search_for_email(self, table_name, eml_fielddata, fname_fielddata,
                         lname_fielddata):
        """Searches for an email address in a airtable database table and
        creates a record if it is not found.

        It takes the table name as input as well as field, data tuples for
        searching and assigment of email, fname, and lname fields.
        """
        eml_field, eml_addr = eml_fielddata
        fname_field, fname = fname_fielddata
        lname_field, lname = lname_fielddata
        try:
            rec_id = self.search_for_rec(table_name, eml_field, eml_addr)
        except exceptions.NoRecordError:
            # create new record if none found
            data = {
                eml_field: eml_addr.lower(),
                fname_field: fname,
                lname_field: lname,
            }
            try:
                self.create(table_name, data)
            except AttributeError:
                logging.exception(("Could not create record. Check database "
                                   "id, API key and table name. Traceback "
                                   "follows:"))
                raise SystemExit(1)
            rec_id = self.search_for_rec(table_name, eml_field, eml_addr)

        # get id for newly created record
        return rec_id

    def create_task_record(self, table_name, text_fielddata, person_fielddata,
                           notes_fielddata=(), attach_fielddata=()):
        """Creates a linked record in a tasks table from data collected from an
        email.

        The record is created from found text, a link to the record for a
        person in a people table, the entire email body from which the text was
        taken and optionally a link to a record of attachments from that email.

        All _fielddata arguments are tuples of a field name and the data for
        that field. Unspecified fields default to empty tuple.
        """
        text_field, text = text_fielddata
        person_field, people = person_fielddata
        # airtable requires record links to be in lists.
        if not isinstance(people, list):
            people = [people]

        # data for record
        data = {
            text_field: text,
            person_field: people,
        }
        # check optional parameters
        if notes_fielddata:
            notes_field, notes = notes_fielddata
            data[notes_field] = notes
        # only attach files if argument is present
        if attach_fielddata:
            attach_field, attach_id = attach_fielddata
            if not isinstance(attach_id, list):
                attach_id = [attach_id]
            data[attach_field] = attach_id

        try:
            self.create(table_name, data)
        except AttributeError:
            logging.exception(("Could not create record. Check database "
                               "id, API key and table name. Traceback "
                               "follows:"))
            raise SystemExit(1)

        return None

    def upload_attach(self, table_name, name_fielddata, files_fielddata):
        """Uploads files to airtable from a list of specified urls to a new record
        and return the 'id' of that record.

        All _fielddata arguments are tuples of a field name and the data for
        that field. Unspecified fields default to empty tuple.
        """
        # get settings
        name_field, name = name_fielddata
        attach_field, urls = files_fielddata

        if not isinstance(urls, list):
            urls = [urls]

        # format urls for airtable to parse
        all_urls = [{"url": url} for url in urls]
        data = {
            name_field: name,
            attach_field: all_urls,
        }
        try:
            self.create(table_name, data)
        except AttributeError:
            logging.exception(("Could not create record. Check database "
                               "id, API key and table name. Traceback "
                               "follows:"))
            raise SystemExit(1)

        # return new rec id
        return self.search_for_rec(table_name, name_field, name)
