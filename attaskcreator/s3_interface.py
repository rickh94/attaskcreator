#!/usr/bin/env python3
# upload files to s3 for redownloading by airtable (feel like a dumbass but it
# works)

import boto3
import os

def s3_make_url(filename, bucket):
    s3 = boto3.client('s3')
    basename = os.path.basename(filename)

    s3.upload_file(filename, bucket, basename)


    url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket,
                'Key': basename
                }
            )
    return url


