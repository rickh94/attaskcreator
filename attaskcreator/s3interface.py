"""Interface to s3 for attaskcreator."""
import os
import boto3


def make_url(filename, bucket):
    """Upload a file to an s3 bucket and return a presigned url for that
    file."""
    s3client = boto3.client('s3')
    basename = os.path.basename(filename)
    s3client.upload_file(filename, bucket, basename)

    return s3client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket,
            'Key': basename
        }
    )
