#!/usr/bin/env python3
# environent variables must already be exported

import boto3


s3 = boto3.client('s3')

bucket = 'BUCKET NAME FROM CONFIG'

s3.upload_file("test.txt", bucket, 'test.txt')
s3.upload_file('dup.png', bucket, 'dup.png')


url1 = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket,
            'Key': 'test.txt'
            }
        )


url2 = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket,
            'Key': 'dup.png'
            }
        )

print(url1)
print(url2)
