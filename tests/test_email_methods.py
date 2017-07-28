"""Testcases for parse_to_field"""
import unittest
from unittest import mock
from datetime import datetime
import email
import os
from attaskcreator import retrievemail

# useful constants
RECIPS = [
    "John Smith <johnsmith@example.com>",
    "Barack Obama <bobama@whitehouse.gov>",
    "Cory Booker <cbooker@senate.gov>",
    "<admin@google.com>",
    "Bill Clinton <bclinton@whitehouse.gov>",
    ]

RECIP_DICTS = [
    {'fname': 'John', 'lname': 'Smith', 'email': 'johnsmith@example.com'},
    {'fname': 'Barack', 'lname': 'Obama', 'email': 'bobama@whitehouse.gov'},
    {'fname': 'Cory', 'lname': 'Booker', 'email': 'cbooker@senate.gov'},
    {'fname': '', 'lname': '', 'email': 'admin@google.com'},
    {'fname': 'Bill', 'lname': 'Clinton', 'email': 'bclinton@whitehouse.gov'},
    ]

HERE = os.path.dirname(__file__)

with open(os.path.join(HERE, 'testeml'), 'br') as e:
    TEST_MSG = email.message_from_bytes(e.read())

class TestEmailMethods(unittest.TestCase):
    """Tests for parse_to_field."""

    def setUp(self):
        pass

    def test_parse_recip(self):
        """Test case for parse_recipient."""
        for num, recip in enumerate(RECIPS):
            self.assertDictEqual(
                retrievemail.parse_recipient(recip),
                RECIP_DICTS[num])

    def test_parse_to(self):
        """Test case for parse_to_field."""
        self.assertListEqual(retrievemail.parse_to_field(', '.join(RECIPS)), RECIP_DICTS)

    def test_save_attach(self):
        """Test saving attachments from an email message."""
        m = mock.mock_open()
        with mock.patch('builtins.open', m, create=True):
            paths = retrievemail.save_attachments(TEST_MSG)
        date = datetime.today().strftime("%Y-%m-%d-")
        #
        filename1 = date + 'atinterface.py'
        filename2 = date + 'README.md'
        filepath1 = os.path.join('/tmp', filename1)
        filepath2 = os.path.join('/tmp', filename2)
        m.assert_any_call(filepath1, 'wb')
        m.assert_any_call(filepath2, 'wb')
        self.assertListEqual([filepath1, filepath2], paths)

    def test_get_msg_text(self):
        """Test getting message content."""
        self.assertRegex(
            retrievemail.get_msg_text(TEST_MSG),
            r'.*?This is a test email\..*?')

    # don't want to bother calling these. tested elsewhere.
    @mock.patch('attaskcreator.retrievemail.get_msg_text')
    @mock.patch('attaskcreator.retrievemail.html2text')
    def test_read_msg_info(self, mock_html2text, mock_get_msg):
        """Test reading a message's info."""
        testmsg = {
            'from': 'test@example.com',
            'to': 'testto@example.com',
            'subject': 'test subject',
            'date': 'test date',
            }
        test_return = retrievemail.read_msg_info(testmsg)
        # these parens are brutal
        assert set(testmsg.items()).issubset(set(test_return.items()))
        # assert method calls
        mock_get_msg.assert_called_once_with(testmsg)
        assert mock_html2text.called
