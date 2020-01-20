import boto3
from botocore.exceptions import ClientError


import sys
import os
from datetime import datetime as dt
import json
import logging
import logging.config

logging.config.fileConfig('config/logging.config')
logger = logging.getLogger()

def get_secret(secret_name, region):
    """Retreive the values from a secret

    :param secret_name: Name of the secret from which values have to be retrieved
    :param region: AWS Region in which secret is present
    """
    secret_retrieval_start=None
    secret_retrieval_end=None

    secret_client = boto3.client('secretsmanager', region_name=region)
    try:
        secret_retrieval_start=dt.now()
        secret_response=secret_client.get_secret_value(SecretId=secret_name)
        secret_object=json.loads(secret_response['SecretString'])
        secret_retrieval_end=dt.now()
        logger.debug(
            str.format('Total time taken to retreive secret {} ' +
                    'details is {} microseconds.',
                secret_name,
                (secret_retrieval_end-secret_retrieval_start).microseconds
            )
        )
        logger.info(
            str.format('Details from secret {} in the region {} are: ' +
                    'username:{} , engine:{} , host:{} , port:{} ',
                secret_name,
                region,
                secret_object['username'],
                secret_object['engine'],
                secret_object['host'],
                secret_object['port']
            )
        )
        return secret_object
    except ClientError as e:
        logging.error(
            str.format('Error encountered in retreieving the secret {} ' +
                    'in the {} region',
                secret_name,
                region
            )
        )
        logging.error(e)
        return None


if __name__=='__main__':
    secret_name=sys.argv[1]
    region=sys.argv[2]
    secret_object=get_secret(secret_name,region)
    if(secret_object==None):
        print("Looks like there is a problem in retreiving the secret.")
    else:
        print("Secret retreived successfully.")
