'''Test cases for parsing message text.'''
import unittest
from unittest import mock
from attaskcreator import create

PHRASES = ['test phrase 1',
           'can you please',
           'TEST UPPER CASE',
           'test phrase 4',
          ]
class TestParseText(unittest.TestCase):
    """Test the text parsing methods for attaskcreator."""

    def test_choose_phrase(self):
        """Tests choosing a phrase for parsing out text from a message."""
        self.assertEqual(
            create.choose_phrase(PHRASES, 'this tests test phrase 1'),
            'test phrase 1')
        self.assertEqual(
            create.choose_phrase(PHRASES, 'Can you please test this out'),
            'can you please')
        self.assertEqual(
            create.choose_phrase(
                PHRASES, 'test upper case if you please'),
            'TEST UPPER CASE')
        self.assertEqual(
            create.choose_phrase(PHRASES, 'this is a test of test phrase 4'),
            'test phrase 4')
        self.assertIsNone(
            create.choose_phrase(
                PHRASES, 'this is a test that returns nothing')
            )

    @mock.patch('attaskcreator.create.choose_phrase')
    def test_parse_message(self, mock_choose_phrase):
        """Test for parse email message."""
        mock_choose_phrase.return_value = 'Can you please'
        self.assertEqual(
            create.parse_email_message(
                (PHRASES, '?'),
                'Can you please return this?'),
            'return this'
            )
        mock_choose_phrase.assert_called_once_with(
            PHRASES, 'Can you please return this?'
            )
        mock_choose_phrase.reset_mock()

        mock_choose_phrase.return_value = 'Would you please'
        self.assertEqual(
            create.parse_email_message(
                (PHRASES, '?'),
                'Would you please return this?'),
            'return this'
            )
        mock_choose_phrase.assert_called_once_with(
            PHRASES, 'Would you please return this?'
            )
        mock_choose_phrase.reset_mock()

        mock_choose_phrase.return_value = None
        self.assertIsNone(
            create.parse_email_message(
                (PHRASES, '?'),
                'This returns nothing?')
            )
        mock_choose_phrase.assert_called_once_with(
            PHRASES, 'This returns nothing?'
            )
