from airflow.decorators import dag, task
from pendulum import datetime

import requests
import pymongo
import pandas as pd

default_args = {"start_date": datetime(2023, 4, 8)}

@dag(schedule="@yearly", default_args=default_args, catchup=False)
def xcom_taskflow_dag():
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
        return {"leagues": json_response}

    @task
    def upload_to_mongo_db(leagues: list):
        client = pymongo.MongoClient(
            host=f"mongodb+srv://ashkenov_a:Yonsei7991@mycluster.2gvwkvc.mongodb.net/?retryWrites=true&w=majority",
            )
        db = client['football_api']
        coll = db['english_leagues']

        coll.insert_many(leagues)

    @task
    def get_english_football_clubs(leagues: list):
        df_league_raw = pd.json_normalize(leagues)
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
        return {"teams": teams_info}
    
    @task
    def upload_to_mongo_db2(teams: list):
        client = pymongo.MongoClient(
            host=f"mongodb+srv://ashkenov_a:Yonsei7991@mycluster.2gvwkvc.mongodb.net/?retryWrites=true&w=majority",
            )
        db = client['football_api']
        coll = db['english_teams']

        coll.insert_many(teams)

    get_english_football_leagues >> [upload_to_mongo_db, get_english_football_clubs] >> upload_to_mongo_db2

xcom_taskflow_dag()
