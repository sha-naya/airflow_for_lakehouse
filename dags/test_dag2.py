from datetime import datetime, date, timedelta

from airflow import DAG
from airflow.decorators import task

import requests
import boto3
import json
import pandas as pd
import pyodbc
import numpy as np

with DAG(
    dag_id="demo_dag2",
    start_date=datetime(2023, 4, 7),
    schedule="@daily"
    ) as dag:

    @task
    def get_data_from_api():
        url = "https://api-basketball.p.rapidapi.com/games"

        querystring = {"date":"2023-02-04"}

        headers = {
            "X-RapidAPI-Key": "95d1d0071fmsh61e56ba2bd00280p11af1ajsna4e07526c0e4",
            "X-RapidAPI-Host": "api-basketball.p.rapidapi.com"
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
            Key='basketball_games.json',
            Body=api_data
        )
    
    @task
    def upload_to_azure_sql():
        conn = pyodbc.connect(
            'Driver={ODBC Driver 18 for SQL Server};Server=tcp:cs779-server.database.windows.net,1433;Database=cs779;Uid=epoch;Pwd=Yonsei7991;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
            )
        cursor = conn.cursor()

        s3 = boto3.resource(
            service_name='s3',
            region_name='us-east-1',
            aws_access_key_id='AKIA4VNTOKW7LDEWF4VW',
            aws_secret_access_key='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',
        )

        s3_object = s3.Bucket('cs779').Object('basketball_games.json').get()['Body'].read()
        s3_json = json.loads(s3_object)
        
        df: pd.DataFrame = pd.json_normalize(s3_json['response'], sep='_')

        df = df.replace(np.nan,0)
        
        for index, row in df.iterrows():
            cursor.execute("INSERT INTO basketball_games (id,date,time,timestamp,timezone,stage,week,status_long,status_short,status_timer,league_id,league_name,league_type,league_season,league_logo,country_id,country_name,country_code,country_flag,teams_home_id,teams_home_name,teams_home_logo,teams_away_id,teams_away_name,teams_away_logo,scores_home_quarter_1,scores_home_quarter_2,scores_home_quarter_3,scores_home_quarter_4,scores_home_over_time,scores_home_total,scores_away_quarter_1,scores_away_quarter_2,scores_away_quarter_3,scores_away_quarter_4,scores_away_over_time,scores_away_total) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            row.id,
            row.date,
            row.time,
            row.timestamp,
            row.timezone,
            row.stage,
            row.week,
            row.status_long,
            row.status_short,
            row.status_timer,
            row.league_id,
            row.league_name,
            row.league_type,
            row.league_season,
            row.league_logo,
            row.country_id,
            row.country_name,
            row.country_code,
            row.country_flag,
            row.teams_home_id,
            row.teams_home_name,
            row.teams_home_logo,
            row.teams_away_id,
            row.teams_away_name,
            row.teams_away_logo,
            row.scores_home_quarter_1,
            row.scores_home_quarter_2,
            row.scores_home_quarter_3,
            row.scores_home_quarter_4,
            row.scores_home_over_time,
            row.scores_home_total,
            row.scores_away_quarter_1,
            row.scores_away_quarter_2,
            row.scores_away_quarter_3,
            row.scores_away_quarter_4,
            row.scores_away_over_time,
            row.scores_away_total
)
        conn.commit()
        cursor.close()

    get_data_from_api() >> upload_to_azure_sql()
