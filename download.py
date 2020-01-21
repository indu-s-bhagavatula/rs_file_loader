import urllib.request
import sys
import os
from datetime import datetime as dt
import logging
import logging.config

logging.config.fileConfig('config/logging.config')
logger = logging.getLogger();

def download_file_httpsrc(url, local_filename):
    """ Download the file from the HTTP location specified into the location.
    urllib library will be used to download the object.

    :param url: URL of the HTTP data source link to download the file
    :local_filename: File name (including the path qualified path) to save the
    file.
    """
    logger.info('Startted downloading file from ' + url +
        ' . Downloading to ' + local_filename )
    download_start=dt.now()
    try:
        urllib.request.urlretrieve(url, local_filename)
        download_end=dt.now()
        logger.debug(
            str.format('Total time taken to download the file'
                ' {} microseconds'
                ' and file size is {} bytes',
                (download_end-download_start).microseconds,
                (os.path.getsize(local_filename))
            )
        )
        logger.info('Finished downloading file from ' + url +
            ' . Downloaded file ' + local_filename )
    except Exception as e:
        logger.error(
            str.join(
                ' ',
                [
                    'Error occurred while downloading the file ' + url + ' ',
                    str(e)
                ]
            ) , 
            exc_info=True
        )
        exit(-1)

def extract_file_from_url(url):
    """ Extracts file name from the given http url

    :param url: URL of the HTTP data source link to download the file
    """
    return url.split("/")[-1]


if __name__=='__main__':
    url=sys.argv[1]
    filename=extract_file_from_url(url)
    download_file_httpsrc(url,"/tmp/"+filename)
