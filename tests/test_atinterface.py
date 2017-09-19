"""Tests interaction with the airtable API through calls to the MyDatabase
class.
"""
import unittest
from unittest import mock
from attaskcreator.atinterface import MyDatabase
from attaskcreator import exceptions


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

    @mock.patch('attaskcreator.atinterface.logging')
    @mock.patch.object(MyDatabase, 'get')
    def test_search_for_rec(self, mock_get, mock_logging):
        """test the search for rec method"""
        mock_get.return_value = {
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
        # find something
        self.assertEqual(
            self.base.search_for_rec('test_table', 'test_field', 'find me'),
            'rec123456789')
        mock_get.assert_called_with('test_table')
        # test case sensitivity
        self.assertEqual(
            self.base.search_for_rec('test_table', 'test_field',
                                     'Find Something eLse'),
            'rec234567891')
        mock_get.assert_called_with('test_table')
        # find nothing
        self.assertRaises(
            exceptions.NoRecordError,
            self.base.search_for_rec,
            'test_table2',
            'test_field',
            'nothing to see here')
        mock_get.assert_called_with('test_table2')
        # fail to get table, raise exception
        mock_get.side_effect = AttributeError
        self.assertRaises(
            SystemExit,
            self.base.search_for_rec,
            'test_table2', 'test_field', 'nothing')
        mock_logging.exception.assert_any_call(mock.ANY)

    @mock.patch('attaskcreator.atinterface.logging')
    @mock.patch.object(MyDatabase, 'create')
    @mock.patch.object(MyDatabase, 'search_for_rec')
    def test_search_for_email(self, mock_search_for_rec, mock_create,
                              mock_logging):
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
        # find nothing and create record
        mock_search_for_rec.side_effect = (exceptions.NoRecordError,
                                           'rec01emf001')
        self.assertEqual(
            self.base.search_for_email(
                'people_table',
                ('email', 'bobama@whitehouse.gov'),
                ('First Name', 'Barack'),
                ('Last Name', 'Obama'),
                ),
            'rec01emf001'
        )
        mock_search_for_rec.assert_any_call('people_table', 'email',
                                            'bobama@whitehouse.gov')
        mock_create.assert_called_with('people_table',
                                       {
                                           'email': 'bobama@whitehouse.gov',
                                           'First Name': 'Barack',
                                           'Last Name': 'Obama',
                                       })
        # fail to create record
        mock_search_for_rec.side_effect = exceptions.NoRecordError
        mock_create.side_effect = AttributeError
        self.assertRaises(
            SystemExit,
            self.base.search_for_email,
            'people_table',
            ('email', 'bobama@whitehouse.gov'),
            ('First Name', 'Barack'),
            ('Last Name', 'Obama')
        )
        mock_logging.exception.assert_any_call(mock.ANY)

    @mock.patch('attaskcreator.atinterface.logging')
    @mock.patch.object(MyDatabase, 'create')
    def test_create_test_record(self, mock_create, mock_logging):
        """Tests for create_task_record."""
        # minimal test
        self.assertIsNone(
            self.base.create_task_record(
                'test table1',
                ('test text field', 'my test text'),
                ('test person field', ['rec123456789']),
                )
            )
        mock_create.assert_called_with('test table1',
                                       {
                                           'test text field': 'my test text',
                                           'test person field':
                                           ['rec123456789'],
                                           'Before leaving work': True,
                                       })
        # tests with some fields
        self.assertIsNone(
            self.base.create_task_record(
                'test table2',
                ('test text field', 'my test text'),
                ('test person field', ['rec123456789']),
                attach_fielddata=('test attachments field', ['rec0009987']),
                )
            )
        mock_create.assert_called_with('test table2',
                                       {
                                           'test text field': 'my test text',
                                           'Before leaving work': True,
                                           'test person field':
                                           ['rec123456789'],
                                           'test attachments field':
                                           ['rec0009987'],
                                       })

        self.assertIsNone(
            self.base.create_task_record(
                'test table2',
                ('test text field', 'my test text'),
                ('test person field', ['rec123456789']),
                ('test notes field', 'these are some notes'),
                )
            )
        mock_create.assert_called_with('test table2',
                                       {
                                           'test text field': 'my test text',
                                           'test person field':
                                           ['rec123456789'],
                                           'Before leaving work': True,
                                           'test notes field':
                                           'these are some notes',
                                       })
        # test with all fields
        self.assertIsNone(
            self.base.create_task_record(
                'test table3',
                ('test text field', 'my test text'),
                ('test person field', ['rec123456789']),
                ('test notes field', 'this is the full\n body of the email'),
                ('test attachments field', ['rec0009987']),
                sender_filter=[('testperson', 'test1'), ('noone', 'test2')],
                sender_info='testperson@wherever.com'
                )
            )
        mock_create.assert_called_with('test table3',
                                       {
                                           'test text field': 'my test text',
                                           'test person field':
                                           ['rec123456789'],
                                           'Before leaving work': True,
                                           'test notes field':
                                           'this is the full\n body of the'
                                           + ' email',
                                           'test attachments field':
                                           ['rec0009987'],
                                           'Type': ['test1'],
                                       })
        # test with all fields
        self.assertIsNone(
            self.base.create_task_record(
                'test table3',
                ('test text field', 'my test text'),
                ('test person field', ['rec123456789']),
                ('test notes field', 'this is the full\n body of the email'),
                ('test attachments field', ['rec0009987']),
                sender_filter=[('testperson', 'test1'), ('noone', 'test2')],
                sender_info='noone@example.com'
                )
            )
        mock_create.assert_called_with('test table3',
                                       {
                                           'test text field': 'my test text',
                                           'test person field':
                                           ['rec123456789'],
                                           'Before leaving work': True,
                                           'test notes field':
                                           'this is the full\n body of the'
                                           + ' email',
                                           'test attachments field':
                                           ['rec0009987'],
                                           'Type': ['test2'],
                                       })
        # links not lists
        self.assertIsNone(
            self.base.create_task_record(
                'test table2',
                ('test text field', 'my second test text'),
                ('test person field', 'rec123456789'),
                attach_fielddata=('test attachments field', 'rec0009987'),
                )
            )
        mock_create.assert_called_with('test table2',
                                       {
                                           'test text field':
                                           'my second test text',
                                           'test person field':
                                           ['rec123456789'],
                                           'Before leaving work': True,
                                           'test attachments field':
                                           ['rec0009987'],
                                       })
        # multiple links
        self.assertIsNone(
            self.base.create_task_record(
                'test table3',
                ('test text field', 'my test text'),
                ('test person field', ['rec123456789', 'rec012345678']),
                ('test notes field', 'this is the full\n body of the email'),
                ('test attachments field', ['rec0009987', 'rec1009987']),
                )
            )
        mock_create.assert_called_with('test table3',
                                       {
                                           'test text field': 'my test text',
                                           'test person field':
                                           ['rec123456789', 'rec012345678'],
                                           'Before leaving work': True,
                                           'test notes field':
                                           'this is the full\n body of the'
                                           + ' email',
                                           'test attachments field':
                                           ['rec0009987', 'rec1009987'],

                                       })
        # fail to connect to table properly
        mock_create.side_effect = AttributeError
        self.assertRaises(
            SystemExit,
            self.base.create_task_record,
            'failtable',
            ('test', 'test'),
            ('othertest', 'othertest')
        )
        mock_logging.exception.assert_any_call(mock.ANY)

    @mock.patch('attaskcreator.atinterface.logging')
    @mock.patch.object(MyDatabase, 'search_for_rec')
    @mock.patch.object(MyDatabase, 'create')
    def test_upload_attach(self, mock_create, mock_search_for_rec,
                           mock_logging):
        """Tests the uploading of attachments."""
        mock_search_for_rec.return_value = 'rec001234567'
        # basic
        self.assertEqual(
            self.base.upload_attach(
                'test attach table',
                ('test name field', 'test record name'),
                ('test attach field', ['http://example.com']),
                ),
            'rec001234567',
            )
        mock_create.assert_called_with(
            'test attach table',
            {
                'test name field': 'test record name',
                'test attach field': [
                    {'url': 'http://example.com'}],
            })
        mock_search_for_rec.assert_called_with(
            'test attach table',
            'test name field',
            'test record name',
            )
        # urls not as list
        self.assertEqual(
            self.base.upload_attach(
                'test attach table',
                ('test name field', 'test record name'),
                ('test attach field', 'http://example.com'),
                ),
            'rec001234567',
            )
        mock_create.assert_called_with(
            'test attach table',
            {
                'test name field': 'test record name',
                'test attach field': [
                    {'url': 'http://example.com'}],
            })
        mock_search_for_rec.assert_called_with(
            'test attach table',
            'test name field',
            'test record name',
            )
        # multiple urls
        self.assertEqual(
            self.base.upload_attach(
                'test attach table',
                ('test name field', 'test record name'),
                ('test attach field', [
                    'http://example.com',
                    'http://google.com',
                    'http://test.passed'
                    ]),
                ),
            'rec001234567',
            )
        mock_create.assert_called_with(
            'test attach table',
            {
                'test name field': 'test record name',
                'test attach field': [
                    {'url': 'http://example.com'},
                    {'url': 'http://google.com'},
                    {'url': 'http://test.passed'}],
            })
        mock_search_for_rec.assert_called_with(
            'test attach table',
            'test name field',
            'test record name',
            )
        # fails to upload to table
        mock_create.side_effect = AttributeError
        self.assertRaises(
            SystemExit,
            self.base.upload_attach,
            'test attach table',
            ('name field', 'record name'),
            ('test attach field', 'http://fail.com')
        )
        mock_logging.exception.assert_any_call(mock.ANY)
