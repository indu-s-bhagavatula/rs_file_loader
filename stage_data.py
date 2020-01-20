import boto3
from botocore.exceptions import ClientError

import sys
import os
from datetime import datetime as dt
import logging
import logging.config

logging.config.fileConfig('config/logging.config')
logger = logging.getLogger()

def upload_to_s3(local_filename, bucket, s3_prefix, region):
    """Upload a file to an S3 bucket

    :param local_filename: File to upload
    :param bucket: Bucket to upload to
    :param s3_prefix: S3 object prefix with which upload.
    :return: True if file was uploaded, else False
    """
    upload_start=None
    upload_end=None
    file_name=local_filename.split('/')[-1]
    # Append '/' if s3_prefix doesn't contain it
    if(s3_prefix[-1]=='/'):
        object_name=s3_prefix+file_name
    else:
        object_name=s3_prefix+'/'+file_name

    s3_client = boto3.client('s3', region_name=region)
    try:
        logger.info(
            str.format('Startted uploading file {} to s3 bukcket - {}' +
                ' with prefix {}',
                local_filename,
                bucket,
                object_name
            )
        )
        upload_start=dt.now()
        response = s3_client.upload_file(local_filename, bucket, object_name)
        upload_end=dt.now()
        logger.debug(
            str.format('Total time taken to upload the file {} to s3 bucket {}' +
                ' with prefix {} is {} microseconds.',
                local_filename,
                bucket,
                object_name,
                (upload_end-upload_start).microseconds
            )
        )
        logger.info(
            str.format('Finished uploading file {} to s3 bukcket - {}' +
                ' with prefix {}',
                local_filename,
                bucket,
                object_name
            )
        )
    except ClientError as e:
        logging.error(
            str.format('Failed uploading file {} to s3 bukcket - {}' +
                ' with prefix {}',
                local_filename,
                bucket,
                object_name
            )
        )
        logging.error(e)
        return False
    return True

if __name__=='__main__':
    local_filenamename=sys.argv[1]
    bucket=sys.argv[2]
    s3_prefix=sys.argv[3]
    region=sys.argv[4]
    file_uploaded=upload_to_s3(local_filenamename, bucket, s3_prefix, region)
    if(file_uploaded):
        print("Upload Successful")
    else:
        print("Upload failed")
