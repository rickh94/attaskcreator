"""Test s3 interface."""
import unittest
from unittest import mock
from botocore.exceptions import BotoCoreError
from attaskcreator import s3interface
from attaskcreator import exceptions


class S3InterfaceTest(unittest.TestCase):

    @mock.patch('attaskcreator.s3interface.daiquiri.getLogger')
    @mock.patch('attaskcreator.s3interface.boto3')
    def test_s3_interface(self, mock_boto3, mock_get_logger):
        mock_s3 = mock.Mock()
        mock_boto3.client.return_value = mock_s3
        # test passes
        s3interface.make_url('/tmp/downloads/2017-07-29-myfile.txt',
                             'mytestbucket')
        mock_boto3.client.assert_called_with('s3')
        mock_s3.upload_file.assert_called_with(
            '/tmp/downloads/2017-07-29-myfile.txt',
            'mytestbucket',
            '2017-07-29-myfile.txt'
            )
        mock_s3.generate_presigned_url.assert_called_with(
            ClientMethod='get_object',
            Params={
                'Bucket': 'mytestbucket',
                'Key': '2017-07-29-myfile.txt',
                }
            )

        # test exceptions
        mock_s3.reset_mock()
        mock_logger = mock.Mock()
        mock_get_logger.return_value = mock_logger
        mock_s3.upload_file.side_effect = BotoCoreError
        self.assertRaises(
            exceptions.NoAttachmentError,
            s3interface.make_url,
            '/tmp/downloads/testfile.txt',
            'mytestbucket')
        mock_boto3.client.assert_called_with('s3')
        mock_logger.error.assert_called()

        mock_s3.reset_mock()
        mock_s3.side_effect = OSError
        self.assertRaises(
            exceptions.NoAttachmentError,
            s3interface.make_url,
            '/tmp/downloads/testfile.txt',
            'mytestbucket')
        mock_boto3.client.assert_called_with('s3')
        mock_logger.error.assert_called()
