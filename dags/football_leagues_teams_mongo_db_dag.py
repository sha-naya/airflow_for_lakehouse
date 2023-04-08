from airflow.decorators import dag, task
from pendulum import datetime

import requests
import pymongo
import pandas as pd
import time

@task
def get_english_football_leagues():
    url = "https://api-football-v1.p.rapidapi.com/v3/leagues"

    querystring = {"country":"England"}

    headers = {
        "X-RapidAPI-Key": "95d1d0071fmsh61e56ba2bd00280p11af1ajsna4e07526c0e4",
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    json_response = response.json()['response']
    return json_response

@task
def upload_to_mongo_db(json_response):
    client = pymongo.MongoClient(
        host=f"mongodb+srv://ashkenov_a:Yonsei7991@mycluster.2gvwkvc.mongodb.net/?retryWrites=true&w=majority",
        )
    db = client['football_api']
    coll = db['english_leagues']

    coll.insert_many(json_response)

@task
def get_english_football_clubs(json_response):
    df_league_raw = pd.json_normalize(json_response)
    df_league = df_league_raw[['league.id', 'league.name', 'league.type']]
    league_ids: set = set(df_league['league.id'])
    teams_info: list = []
    for league in league_ids:
        time.sleep(2)
        url = "https://api-football-v1.p.rapidapi.com/v3/teams"

        querystring = {"league":league,"season":"2022"}

        headers = {
            "X-RapidAPI-Key": "95d1d0071fmsh61e56ba2bd00280p11af1ajsna4e07526c0e4",
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        teams_info.extend(response.json()['response'])
    return teams_info

@task
def upload_to_mongo_db2(teams_info):
    client = pymongo.MongoClient(
        host=f"mongodb+srv://ashkenov_a:Yonsei7991@mycluster.2gvwkvc.mongodb.net/?retryWrites=true&w=majority",
        )
    db = client['football_api']
    coll = db['english_teams']

    coll.insert_many(teams_info)

default_args = {"start_date": datetime(2023, 4, 8)}

@dag(dag_id='english_leagues_teams_dag', schedule_interval='@once', default_args=default_args, catchup=False)
def english_leagues_teams_dag():
    task_1 = get_english_football_leagues()
    task_2 = upload_to_mongo_db(task_1)
    task_3 = get_english_football_clubs(task_1)
    task_4 = upload_to_mongo_db2(task_3)

dag = english_leagues_teams_dag()
