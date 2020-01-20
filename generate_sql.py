import agate
import agatesql

import sys
import os
from datetime import datetime as dt
import logging
import logging.config

logging.config.fileConfig('config/logging.config')
logger = logging.getLogger()

# Redshift is PostgreSQL based and so that dialect can be used.
DIALECT='postgresql'

def generate_sql_from_csv(local_filename, table_name, schema_name
    , uppercase_allowed='None'):
    """ Use agate to parse the SQL file and generate the SQL for PostgreSQL
    dialect.

    :param local_filename: File to be parsed
    :param table_name: Table name in the database
    :param schema_name: Schema name in the database
    :param uppercase_allowed: If set to 'y' then the column names generated
    in the extracted SQL will be allowed to retain upper case letters otherwise
    everything will be converted to lowercase.
    """
    download_start=dt.now()
    table=agate.Table.from_csv(local_filename)
    sql_statement=table.to_sql_create_statement(
        table_name=table_name,
        dialect=DIALECT,
        db_schema=schema_name)
    download_end=dt.now()
    logger.debug(
        str.format('Total time taken to generate sql in {} microseconds',
            (download_end-download_start).microseconds
        )
    )
    if (uppercase_allowed=='y'):
        logger.info(
            str.format("""Generated SQL statement :\n{}""",
            sql_statement
            )
        )
        return sql_statement
    # convert to lower case
    logger.info(
        str.format("""Generated SQL statement :\n{}""",
        sql_statement.lower()
        )
    )
    return sql_statement.lower()

if __name__=='__main__':
    local_filename=sys.argv[1]
    table_name=sys.argv[2]
    schema_name=sys.argv[3]
    uppercase_allowed='n'
    if(len(sys.argv)>=5 and sys.argv[4]=='y'):
        uppercase_allowed='y'

    sql_statement=generate_sql_from_csv(
        local_filename,
        table_name,
        schema_name,
        uppercase_allowed
    )
