"""Testcases for parse_to_field"""
import unittest
from unittest import mock
from datetime import datetime
import email
import os
from attaskcreator import retrievemail

HERE = os.path.dirname(__file__)


class TestEmailMethods(unittest.TestCase):
    """Tests for parse_to_field."""

    def setUp(self):
        """setup TestEmailMethods."""
        with mock.patch.object(retrievemail.FetchMail, '__init__')\
            as mock_init:
            mock_init.return_value = None
            self.testmail = retrievemail.FetchMail('test.example.com')
        with open(os.path.join(HERE, 'testeml'), 'br') as e:
            self.testmsg = email.message_from_bytes(e.read())
        self.recips = [
            "John Smith <johnsmith@example.com>",
            "Barack Obama <bobama@whitehouse.gov>",
            "Cory Booker <cbooker@senate.gov>",
            "<admin@google.com>",
            "Bill Clinton <bclinton@whitehouse.gov>",
            ]
        self.recip_dicts = [
            {'fname': 'John', 'lname': 'Smith', 'email': 'johnsmith@example.com'},
            {'fname': 'Barack', 'lname': 'Obama', 'email': 'bobama@whitehouse.gov'},
            {'fname': 'Cory', 'lname': 'Booker', 'email': 'cbooker@senate.gov'},
            {'fname': '', 'lname': '', 'email': 'admin@google.com'},
            {'fname': 'Bill', 'lname': 'Clinton', 'email': 'bclinton@whitehouse.gov'},
            ]


    @mock.patch.object(retrievemail.FetchMail, 'select')
    @mock.patch.object(retrievemail.FetchMail, 'login')
    def test_select_inbox(self, mock_login, mock_select):
        """test selecting the inbox automatically"""
        self.testmail.select_inbox('testuser', 'password')
        mock_login.assert_called_once_with('testuser', 'password')
        mock_select.assert_called_once_with('Inbox')


    @mock.patch.object(retrievemail.email, 'message_from_bytes')
    @mock.patch.object(retrievemail.FetchMail, 'close')
    @mock.patch.object(retrievemail.FetchMail, 'fetch')
    @mock.patch.object(retrievemail.FetchMail, 'search')
    @mock.patch.object(retrievemail.FetchMail, 'select_inbox')
    def test_fetch_unread_messages(self, mock_select_inbox, mock_search,
                                   mock_fetch, mock_close, mock_message_from_bytes):
        """Test fetching unread messages"""
        # return one message
        mock_search.return_value = ('OK', [b'1'])
        mock_fetch.return_value = ('OK', [['', 'testmsg']])
        mock_message_from_bytes.return_value = self.testmsg
        self.assertEqual(
            self.testmail.fetch_unread_messages('testuser', 'password'),
            [self.testmsg]
            )
        mock_select_inbox.assert_called_once_with('testuser', 'password')
        mock_search.assert_called_once_with(None, 'UnSeen')
        mock_fetch.assert_called_once_with(b'1', '(RFC822)')
        mock_message_from_bytes.assert_called_once_with('testmsg')


    def test_save_attach(self):
        """Test saving attachments from an email message."""
        m = mock.mock_open()
        with mock.patch('builtins.open', m, create=True):
            paths = retrievemail.save_attachments(self.testmsg)
        date = datetime.today().strftime("%Y-%m-%d-")

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
            retrievemail.get_msg_text(self.testmsg),
            r'.*?This is a test email\..*?')


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


    def test_parse_to(self):
        """Test case for parse_to_field."""
        self.assertListEqual(retrievemail.parse_to_field(', '.join(self.recips)),
                             self.recip_dicts)


    def test_parse_recip(self):
        """Test case for parse_recipient."""
        for num, recip in enumerate(self.recips):
            with self.subTest(num=num, recip=recip):
                self.assertDictEqual(retrievemail.parse_recipient(recip),
                                     self.recip_dicts[num])


    @mock.patch('attaskcreator.retrievemail.smtplib.SMTP')
    def test_send_msg(self, mock_smtp):
        retrievemail.sendmsg(
            mock_smtp,
            ('test', 'password'),
            ('Barack Obama', 'bobama@whitehouse.gov'),
            ('Joe Biden', 'jbiden@whitehouse.gov'),
            ('Hey Joe',
             "Isn't it relaxing not to be governing anymore?")
            )
        mock_smtp.login.assert_called_once_with('test', 'password')
        mock_smtp.sendmail.assert_called_once_with(
            "Barack Obama <bobama@whitehouse.gov>",
            "Joe Biden <jbiden@whitehouse.gov>",
            # i would prefer to pass an actual object but the unique ids make
            # that really annoying.
            mock.ANY)
