import plotly.express as px
from pathlib import Path
import datetime as dt
import pandas as pd
import sqlite3

def add_chart_power(df):
    '''
    Adds the chart_power column to a daily_chart df
    Chart Power is an inverse of position. 1=20,2=19 ... 19=2,20=1
    '''
    #df = 
    df.position = pd.to_numeric(df.position)
    df['power'] = 21 - df.position
    return df

def to_dataframe(table_name, chartpower='y'):
    '''
    The parameter should be a select * from table query. It will turn one
    of the spotify.db tables into a Pandas DF
        select * from daily_tracks
        select * from daily_artists
    '''
    query = f'select * from {table_name};'

    conn = sqlite3.connect('/home/flambuth/fredlambuth.com/spotify.db')
    listofDicts = []
    with conn:
            conn.row_factory = sqlite3.Row
            curs = conn.cursor()
            curs.execute(query)
            rows = curs.fetchall()
            for row in rows:
                row_dict = {i: row[i]for i in row.keys()}
                listofDicts.append(row_dict)
    df =  pd.DataFrame(listofDicts).set_index('id')
    df['date'] = pd.to_datetime(df['date'])

    if chartpower=='y':
        return add_chart_power(df)
    else:
        return df

def last_month_charts(df):
    prev_month_num = dt.date.today().month - 1
    current_year = dt.date.today().year
    last_month = (df['date'].dt.month == prev_month_num)&(df['date'].dt.year == current_year)
    df = df[last_month]
    return df


class Daily_Hits:

    def __init__(self):
        self.tracks = to_dataframe('daily_tracks')
        self.artists = to_dataframe('daily_artists')
        self.prev_month_tracks = last_month_charts(self.tracks)
        self.prev_month_artists = last_month_charts(self.artists)
        #returns a tuple of (art_name, song_name)
        self.last_month_top_song = self.prev_month_tracks.groupby(['art_name','song_name']).count().sort_values('power', ascending=False).head(1).index[0]




