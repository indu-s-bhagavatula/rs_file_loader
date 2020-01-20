Load specifier
{
  "source":{
    "format": "string", #Possible values - csv
    "sourceProtocol" : "string", #Possible values - http, https
    "location" : "string" #location of the file -   
  },
  "stg_data":{
    "s3bckt": "string", #S3 bucket
    "s3prefix": "string" #S3 keyprefix
  }
  "destination":{
    "clusterendpoint" : "string", #Full DNS Endpoint of the cluster
    "rsIamRoleArn" : "string", #Redshift IAM Role that is attached to the cluster to be used to in the COPY command
    "secretid": "string", #Identifier of the secret
    "secretregion" : "string" #Region in which AWS Secret is stored.
  },
  "mode": "DROP|TRUNCATE|APPEND"
}

Makes it easy to CSV file from the specified location into the Redshift cluster.
# Modules
## Downloader module
Downloads the file from external repository specified.
This module allows the file to be downloaded from the HTTP location specified to the local system.
## SQL Generator module
Makes use of Python's agate module to generate the table DDL using the file downloaded and generate PostgreSQL statements.  
## S3 Uploader module
The file downloaded
Requires necessary privileges to upload the files into the S3 location
## Table loader module
Makes use of AWS Secret Manager to retrieve the credentials for the cluster to run SQL table create table statement and then run COPY command to load the data. The COPY command will use the IAM Role attached to the cluster.



# Linux commands
## Local to S3 sync
aws s3 sync rs_file_loader s3://indubh-redshift-bulkdata/kumo/rs_file_loader


# On EC2 box
cd $HOME/myapps/rs_file_loader
rm -rf *
aws s3 sync s3://indubh-redshift-bulkdata/kumo/rs_file_loader .
pip install -r requirements.txt --target .

# Sync logging configuration
cd $HOME/myapps/rs_file_loader
rm -rf ./config/*
aws s3 sync s3://indubh-redshift-bulkdata/kumo/rs_file_loader/config ./config

# fix futures module issue
cd $HOME/myapps/rs_file_loader
rm -rf ./concurrent/futures
pip install futures --target ./concurrent/


rm $HOME/
python3 ./download.py 'https://people.sc.fsu.edu/~jburkardt/data/csv/cities.csv'
python3 ./download.py 'http://samplecsvs.s3.amazonaws.com/SalesJan2009.csv'

python3 ./generate_sql.py '/tmp/SalesJan2009.csv' "mytable" "myschema" "y"
python3 ./generate_sql.py '/tmp/SalesJan2009.csv' "mytable" "myschema" "n"

python3 ./generate_sql.py '/tmp/cities.csv' "mytable" "myschema" "y"
python3 ./generate_sql.py '/tmp/cities.csv' "mytable" "myschema"


python3 ./stage_data.py '/tmp/cities.csv' 'indubh-redshift-bulkdata' 'kumo/test_data/rs_file_loader' 'us-east-1'
python3 ./stage_data.py '/tmp/SalesJan2009.csv' 'indubh-redshift-bulkdata' 'kumo/test_data/rs_file_loader' 'us-east-1'


python3 ./retreive_secret.py 'secret_copyperf_rs_file_loader' 'us-east-1'


python3 ./load_data.py
