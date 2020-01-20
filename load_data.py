import boto3
from botocore.exceptions import ClientError
import pg8000

import sys
import os
from pathlib import Path
from datetime import datetime as dt
import json
#import traceback
import logging
import logging.config

import download
import stage_data
import generate_sql
import retreive_secret

logging.config.fileConfig('config/logging.config')
logger = logging.getLogger()

EXCEPTION_TRACE_FILE_LOCATION=str.join(
        '',
        [
            str(Path.home()),
            '/applogs/rs_file_loader/rs_file_loader_trace_',
            str(os.getpid()),
            '.log'
        ]
    )

def load_file_from_s3(
        host, port, database, user_name, password,
        schema_name, table_name, s3file, **kwargs
    ):
    """Retreive the values from a secret

    :param host: Redshift cluster DNS endpoint
    :param port: Port
    :param database: Database name
    :param user_name: User name
    :param password: Password
    :param schema_name: Schema
    :param table_name: Table name
    :param s3file: S3 location of the file(s)
    :param **table_sql: Optional create table statement
    :param **load_mode: Load mode. TRUNCATE - Truncates the table,
    APPEND - Append data to the existing table, DROP - DROP the table
    """
    secret_retrieval_start=None
    secret_retrieval_end=None

    secret_client = boto3.client('secretsmanager', region_name=region)
    try:
        secret_retrieval_start=dt.now()
        secret_response=secret_client.get_secret_value(SecretId=secretname)
        secret_object=json.loads(secret_response['SecretString'])
        secret_retrieval_end=dt.now()
        logger.debug(
            str.format('Total time taken to retreive secret {} ' +
                    'details is {} microseconds.',
                secretname,
                (secret_retrieval_end-secret_retrieval_start).microseconds
            )
        )
        logger.info(
            str.format('Details from secret {} in the region {} are: ' +
                    'user_name:{} , engine:{} , host:{} , port:{} ',
                secretname,
                region,
                secret_object['user_name'],
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
                secretname,
                region
            )
        )
        logging.error(e)
        return None

def parse_config_load(config_file):
    """Parses the specified file and starts the load process
    Sequence of actions:
    1. Parse config
    2. Download the file
    3. Extract DDL if DROP option is used
    4. Stage it on S3
    5. Retrieving secret
    6. Connect to the database and run SQL statements
    """
    # Step 1. Parsing the config file
    try:
        loader_config=json.load(open(config_file))
        logger.info(
            str.format('Load configuration: {}', json.dumps(loader_config))
        )
    except Exception as e:
        logger.error(e, exc_info=True)
        exit(-1)
    # Step 2. Verify the protocol and fetch the file
    if (
        loader_config['source']['sourceProtocol']=='http' or
        loader_config['source']['sourceProtocol']=='https'
    ):
        url=loader_config['source']['location']
        filename=download.extract_file_from_url(url)
        download.download_file_httpsrc(url,"/tmp/"+filename)
    else:
        logger.error(
            str.format(
                'Invalid protocol specified {}',
                loader_config['source']['sourceProtocol']
            )
        )
        exit(-1)

if __name__=='__main__':
    config_file='config/rs_file_loader.config'
    logger.debug(
        str.format(
            'Exception trace file - {}',
            EXCEPTION_TRACE_FILE_LOCATION
        )
    )
    parse_config_load(config_file)
