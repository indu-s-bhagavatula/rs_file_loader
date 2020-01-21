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

def load_file_from_s3(
        secret_name, secret_region, database, 
        schema_name, table_name, s3file, s3_region, **kwargs
    ):
    """Retreive the values from a secret

    :param secret_name: secretid that contains the connection string and other
    details
    :param secret_region: secret region
    :param database: Database name
    :param schema_name: Schema
    :param table_name: Table name
    :param s3file: S3 location of the file(s)
    :param region: S3 bucket region
    :param **table_sql: Optional create table statement
    :param **load_mode: Load mode. TRUNCATE - Truncates the table,
    APPEND - Append data to the existing table, DROP - DROP the table
    """
    secret_retrieval_start=None
    secret_retrieval_end=None

    secret_client = boto3.client('secretsmanager', region_name=secret_region)
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
                    'user_name:{} , engine:{} , host:{} , port:{} ',
                secret_name,
                secret_region,
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
                secret_name,
                secret_region
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
    4. Stage the file on S3
    5. Retrieving secret
    6. Connect to the database and run SQL statements
    """
    
    filename=None
    sql_text=None
    
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
        loader_config['source']['source_protocol']=='http' or
        loader_config['source']['source_protocol']=='https'
    ):
        url=loader_config['source']['location']
        filename="/tmp/"+download.extract_file_from_url(url)
        download.download_file_httpsrc(url,filename)
    else:
        logger.error(
            str.format(
                'Invalid protocol specified {}',
                loader_config['source']['source_protocol']
            )
        )
        exit(-1)
    
    #Step 3. Extract DDL if DROP option is specified in the config file 
    if(loader_config['destination']['load_mode'].lower()=='drop'):
        schema_name=loader_config['destination']['schema_name']
        table_name=loader_config['destination']['table_name']
        sql_text=generate_sql.generate_sql_from_csv(
            local_filename=filename,
            table_name=table_name,
            schema_name=schema_name,
            upper_case_allowed=loader_config['destination']['upper_case_allowed']
        )
    else:
        schema_name=loader_config['destination']['schema_name']
        table_name=loader_config['destination']['table_name']
        sql_text=generate_sql.generate_sql_from_csv(
            local_filename=filename,
            table_name=table_name,
            schema_name=schema_name
        )
    
    #Step 4 - Stage the data on S3
    s3_bucket=loader_config['stg_data']['s3_bucket']
    s3_prefix=loader_config['stg_data']['s3_prefix']
    s3_region=loader_config['stg_data']['s3_prefix']
    is_file_uploaded=stage_data.upload_to_s3(
        local_filename=filename,
        s3_bucket=s3_bucket
        s3_prefix=s3_prefix
    )
    if(! is_file_uploaded):
        exit(-1)
    
    #TODO: 5. Retrieving secret
    #TODO: 6. Connect to the database and run SQL statements


if __name__=='__main__':
    config_file='config/rs_file_loader.config'
    parse_config_load(config_file)
