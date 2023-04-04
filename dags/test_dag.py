from datetime import datetime

from airflow import DAG
from airflow.decorators import task

import requests
import pymongo
import boto3
import json

with DAG(
    dag_id="demo_dag",
    start_date=datetime(2023, 4, 1),
    schedule="0 0 * * *"
    ) as dag:

    @task
    def get_data_from_api():
        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

        querystring = {"date":"2023-02-06"}

        headers = {
            "X-RapidAPI-Key": "95d1d0071fmsh61e56ba2bd00280p11af1ajsna4e07526c0e4",
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        json_response = response.json()

        api_data = json.dumps(json_response, indent=4)

        s3 = boto3.resource(
            service_name='s3',
            region_name='us-east-1',
            aws_access_key_id='AKIA4VNTOKW7LDEWF4VW',
            aws_secret_access_key='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',
        )
        
        s3_bucket = s3.Bucket(name='cs779')

        s3_bucket.put_object(
            Key='api_data.json',
            Body=api_data
        )
    
    @task
    def upload_to_mongo_db():
        client = pymongo.MongoClient(
            host=f"mongodb+srv://ashkenov_a:Yonsei7991@mycluster.2gvwkvc.mongodb.net/?retryWrites=true&w=majority",
            )

        db = client['football_api']
        coll = db['fixtures']

        s3 = boto3.resource(
            service_name='s3',
            region_name='us-east-1',
            aws_access_key_id='AKIA4VNTOKW7LDEWF4VW',
            aws_secret_access_key='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',
        )

        s3_object = s3.Bucket('cs779').Object('api_data.json').get()['Body'].read()
        s3_json = json.loads(s3_object)

        print(type(s3_object))
        print(s3_object)

        coll.insert_many(s3_json['response'])

    get_data_from_api() >> upload_to_mongo_db()
