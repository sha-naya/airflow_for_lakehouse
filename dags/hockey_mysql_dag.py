from airflow.decorators import dag, task
#from pendulum import datetime
from datetime import datetime, date, timedelta

import requests
import pymysql
import pandas as pd

@task
def get_hockey_matches():
    url = "https://api-hockey.p.rapidapi.com/games/"
    date_yesterday = str(date.today() - timedelta(days=1))
    querystring = {"date":date_yesterday}

    headers = {
        "X-RapidAPI-Key": "95d1d0071fmsh61e56ba2bd00280p11af1ajsna4e07526c0e4",
        "X-RapidAPI-Host": "api-hockey.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    json_response = response.json()
    return json_response

@task
def upload_to_mysql(json_response):
    host_url="mysql-db.clnepvfqmsjh.us-east-1.rds.amazonaws.com"
    port=3306
    user="admin"
    database="hockey_data"
    passwd='kwZQXExJUB4s6PY1XOM6'

    conn =  pymysql.connect(host=host_url, user=user, passwd=passwd, port=port, database=database)

    json_response_norm = pd.json_normalize(json_response['response'], sep='_')

    json_response_norm.to_sql(con=conn, name='hockey_matches_raw', if_exists='append', flavor='mysql')

default_args = {"start_date": datetime(2023, 4, 20)}

@dag(dag_id='hockey_mysql_dag', schedule_interval='@daily', default_args=default_args, catchup=False)
def hockey_matches_dag():
    task_1 = get_hockey_matches()
    task_2 = upload_to_mysql(task_1)

dag = hockey_matches_dag()
