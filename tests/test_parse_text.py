'''Test cases for parsing message text.'''
import unittest
from unittest import mock
from attaskcreator import create
from attaskcreator import exceptions

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
            create.choose_phrase(PHRASES, ('----Begin Forwarded Message\n'
                                           'Some random stuff\n'
                                           'Can you please\nreturn this text'
                                           )),
            'can you please')
        self.assertEqual(
            create.choose_phrase(
                PHRASES, 'test upper case if you please'),
            'TEST UPPER CASE')
        self.assertEqual(
            create.choose_phrase(PHRASES, 'this is a test of test phrase 4'),
            'test phrase 4')
        self.assertRaises(
            exceptions.NoPhraseError,
            create.choose_phrase,
            PHRASES,
            'this is a test that returns nothing'
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
            PHRASES, 'Can you please return this'
            )
        mock_choose_phrase.reset_mock()

        # test with newlines
        self.assertEqual(
            create.parse_email_message(
                (PHRASES, '?'),
                ('---Begin Forwarded Message---\n'
                 'This is a test.\n'
                 'Can you please\nreturn this?')),
            'return this')
        mock_choose_phrase.assert_called_once_with(
            PHRASES, ('---Begin Forwarded Message--- '
                      'This is a test. '
                      'Can you please return this')
            )
        mock_choose_phrase.reset_mock()

        # test with signature as termination
        self.assertEqual(
            create.parse_email_message(
                (PHRASES, '\ndh'),
                ('---Begin Forwarded Message---\n'
                 'This is a test.\n'
                 'Can you please\nreturn this?\ndh')),
            'return this?')

        mock_choose_phrase.assert_called_once_with(
            PHRASES, ('---Begin Forwarded Message--- '
                      'This is a test. '
                      'Can you please return this?')
            )
        mock_choose_phrase.reset_mock()

        # would you please
        mock_choose_phrase.return_value = 'Would you please'
        self.assertRaises(
            exceptions.RegexFailedError,
            create.parse_email_message,
            (PHRASES, '?'),
            'Would you please?',
            )
        mock_choose_phrase.assert_called_once_with(
            PHRASES, 'Would you please'
            )
        mock_choose_phrase.reset_mock()

        # fail to get phrase, exception should propogate up
        mock_choose_phrase.side_effect = exceptions.NoPhraseError(
            "Phrase was not found in the text.")
        self.assertRaises(
            exceptions.NoPhraseError,
            create.parse_email_message,
            (PHRASES, '?'),
            'This returns nothing?'
            )
        mock_choose_phrase.assert_called_once_with(
            PHRASES, 'This returns nothing'
            )
