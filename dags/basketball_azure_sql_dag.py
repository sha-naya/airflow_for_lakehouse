from datetime import datetime, date, timedelta

from airflow import DAG
from airflow.decorators import task

import requests
import boto3
import pandas as pd
from io import StringIO 

with DAG(
    dag_id="basketball_azure_sql_dag",
    start_date=datetime(2023, 4, 7),
    schedule="@daily"
    ) as dag:

    @task
    def get_data_and_drop_in_s3():
        url = "https://api-basketball.p.rapidapi.com/games"
        date_yesterday = str(date.today() - timedelta(days=1))
        querystring = {"date":date_yesterday}
        headers = {
            "X-RapidAPI-Key": "95d1d0071fmsh61e56ba2bd00280p11af1ajsna4e07526c0e4",
            "X-RapidAPI-Host": "api-basketball.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        json_response = response.json()

        csv_buffer = StringIO()
        df: pd.DataFrame = pd.json_normalize(json_response['response'], sep='_')
        df.to_csv(csv_buffer, index=False)

        s3 = boto3.resource(
            service_name='s3',
            region_name='us-east-1',
            aws_access_key_id='AKIA4VNTOKW7LDEWF4VW',
            aws_secret_access_key='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',
        )
        s3_bucket = s3.Bucket(name='cs779')

        s3_bucket.put_object(
            Key='basketball_games.csv',
            Body=csv_buffer.getvalue()
        )

    get_data_and_drop_in_s3()
