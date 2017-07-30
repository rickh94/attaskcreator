"""Tests interaction with the airtable API through calls to the MyDatabase
class."""
import unittest
from unittest import mock
from attaskcreator.atinterface import MyDatabase


DUMMY_RECORDS = {
    "records": [
        {
            "fields": {
                "test_field": "find me",
                "test_field2": "don't find me",
                },
            "id": "rec123456789",
        },
        {
            "fields": {
                "test_field": "find something else",
                },
            "id": "rec234567891",
        },
    ],
}


class MyDatabaseTest(unittest.TestCase):
    """Tests MyDatabase."""

    def setUp(self):
        self.base = MyDatabase('test_id', 'testkey')

    @mock.patch.object(MyDatabase, 'get')
    def test_search_for_rec(self, mock_get):
        """test the search for rec method"""
        mock_get.return_value = DUMMY_RECORDS
        # find something
        self.assertEqual(
            self.base.search_for_rec('test_table', 'test_field', 'find me'), 
            'rec123456789')
        mock_get.assert_called_with('test_table')
        # find something else
        self.assertEqual(
            self.base.search_for_rec('test_table', 'test_field', 
                'find something else'), 
            'rec234567891')
        mock_get.assert_called_with('test_table')
        # find nothing
        self.assertIsNone(
            self.base.search_for_rec('test_table2', 'test_field', 
                'nothing to see here') 
            )
        mock_get.assert_called_with('test_table2')

        
    @mock.patch.object(MyDatabase, 'create')
    @mock.patch.object(MyDatabase, 'search_for_rec')
    def test_search_for_email(self, mock_search_for_rec, mock_create):
        """Tests search_for_email."""
        # find something
        mock_search_for_rec.return_value = 'rec01emf000'
        self.assertEqual(
            self.base.search_for_email(
                'people_table',
                ('email', 'test@example.com'),
                ('First Name', 'John'),
                ('Last Name', 'Smith'),
            ),
            'rec01emf000')
        mock_search_for_rec.assert_called_with('people_table', 'email',
                                               'test@example.com')
        # find nothing
        mock_search_for_rec.return_value = None
        self.assertIsNone(
            self.base.search_for_email(
                'people_table',
                ('email', 'bobama@whitehouse.gov'),
                ('First Name', 'Barack'),
                ('Last Name', 'Obama'),
                ))
        mock_search_for_rec.assert_any_call('people_table', 'email',
                                            'bobama@whitehouse.gov')
        mock_create.assert_called_with('people_table',
                                       {
                                           'email': 'bobama@whitehouse.gov',
                                           'First Name': 'Barack',
                                           'Last Name': 'Obama',
                                       })
