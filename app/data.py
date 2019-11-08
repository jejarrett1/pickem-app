import json
import requests
import pandas as pd
from datetime import datetime

url = r'https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?' \
 \
      r'lang=en' \
 \
      r'&region=us' \
 \
      r'&calendartype=blacklist' \
 \
      r'&limit=300' \
 \
      r'&showAirings=true' \
 \
      r'&dates=2019' \
 \
      r'&seasontype=2' \
 \
      r'&week={week}'

def top_25(week):
    data = requests.get(url.format(week=week))
    d = json.loads(data.text)

    df = pd.DataFrame(d['events'])
    comps = df.competitions.apply(pd.Series)
    comps = comps[0].apply(pd.Series)

    awayTeams = comps.competitors.str[0].apply(pd.Series)
    df['awayRank'] = pd.Series([t.get('current') for t in awayTeams.curatedRank])
    df['awayScore'] = awayTeams.score
    homeTeams = comps.competitors.str[1].apply(pd.Series)
    df['homeRank'] = pd.Series([t.get('current') for t in homeTeams.curatedRank])
    df['homeScore'] = homeTeams.score
    df[['homeTeam', 'awayTeam']] = pd.DataFrame(df.name.str.split(' at ').to_list(), index=df.index)

    return df



# def get_start_stop(week):
#     data = requests.get(url.format(week=week))
#     d = json.loads(data.text)
#     events = d.get('events')[0]
#     competitions = events.get('competitions')[0]
#     for i in range(len(competitions)):
#         competitors = competitions.get('competitors')
#         home_score = competitors[0].get('score')
#         away_score =competitors[1].get('score')
#         print (competitors)
#         print (home_score)
#         print(away_score)


def main(week):
    games = top_25(week)
    return games






