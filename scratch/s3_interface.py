#!/usr/bin/env python3
# environent variables must already be exported

import boto3
import configparser
import os
from airtable import airtable

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

def at_upload_attach(
        base_id, 
        api_key, 
        name_field, 
        rec_name,
        attach_field,
        upload_table,
        *urls
        ):

    at = airtable.Airtable(base_id, api_key)

    all_urls = []

    for url in urls:
        all_urls.append({"url": url})

    data = {
            name_field: rec_name,
            attach_field: all_urls
            }

    at.create(upload_table, data)


config = configparser.ConfigParser()

config.read('test.conf')

os.environ['AWS_ACCESS_KEY_ID'] = config['AWS']['access key id']
os.environ['AWS_SECRET_ACCESS_KEY'] = config['AWS']['secret access key']

my_url1 = s3_make_url("CGVY8227.png", config['AWS']['Bucket'])
my_url2 = s3_make_url("IMG_2825.JPG", config['AWS']['Bucket'])
# print(my_url)
at_upload_attach(
        config['Airtable']['database id'],
        config['Airtable']['api key'],
        config['Airtable']['Name Field'],
        "multiple attachments",
        config['Airtable']['Attachment Field'],
        config['Airtable']['Insert Table'],
        my_url1, 
        my_url2,
        )
