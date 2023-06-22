import boto3
from dotenv import load_dotenv
import os
import psycopg2

# credentials
load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = 'us-east-1'

def load():
    # boto3 client for Redshift
    redshift_client = boto3.client('redshift', aws_access_key_id=AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                region_name=AWS_REGION)

    # redshift Connection details
    redshift_endpoint = os.getenv("REDSHIFT_ENDPOINT")
    redshift_port = os.getenv("REDSHIFT_PORT")
    redshift_database = os.getenv("REDSHIFT_DATABASE")
    redshift_user = os.getenv("REDSHIFT_USER")
    redshift_password = os.getenv("REDSHIFT_PASSWORD")


    #setting up connection with redshift
    redshift_conn = psycopg2.connect(
        host=redshift_endpoint,
        port=redshift_port,
        database=redshift_database,
        user=redshift_user,
        password=redshift_password
    )


    # Define the table structure in your Redshift cluster to match the transformed data's schema.
    table_name = 'Weather'

    create_table_query = """
    CREATE TABLE IF NOT EXISTS {} (
        Country VARCHAR(50),
        City_name VARCHAR(50),
        weather VARCHAR(50),
        Temperature VARCHAR(50),
        Wind VARCHAR(50),
        Sunrise VARCHAR(50),
        Sunset VARCHAR(50)
    );
    """.format(table_name)

    with redshift_conn.cursor() as cursor:
        cursor.execute(create_table_query)
        redshift_conn.commit()


    # Use the COPY command to load the transformed data from the CSV file into the destination table in Redshift.
    csv_file_path = 's3://mybucket-210623/weather_data.csv'

    copy_query = """
    COPY {} FROM '{}' 
    CREDENTIALS 'aws_access_key_id={};aws_secret_access_key={}' 
    CSV IGNOREHEADER 1;
    """.format(table_name, csv_file_path, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

    with redshift_conn.cursor() as cursor:
        cursor.execute(copy_query)
        redshift_conn.commit()

    redshift_conn.close()