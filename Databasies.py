import sqlite3
from Spotifies import new_artist_info
from Genresie import assign_master_genre
from datetime import date

def make_question_marks(cols):
    '''
    Returns the string with the right amount of ?s and commas in between them for a SQL INSERT statement
    '''
    n = len(cols)
    marks = '?,'*n
    marks = marks[:-1]
    return marks

def make_insert_query(table, col_names):
    '''
    Creates a SQLite3 friendly insert statement that can fit on any of the 4 tables stashed as an object variable.
    '''
    marks = make_question_marks(col_names)
    col_string = ','.join(col_names)
    insert_sql = f'''INSERT INTO {table} ({col_string}) VALUES ({marks}) '''
    return insert_sql

def query_db(query, db='my_spotipy.db'):
    '''
    Returns a set of .fetchall() restults from the db

    YOU NEED TO MIGRATE BEFORE THIS CAN WORK! (july 16,2022)
    '''
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        return results
        #cursor.close()
    except sqlite3.Error as error:
        print("I don't know what happened. Maybe you do?", error)
    finally:
        if (conn):
            conn.close()

def fetch_latest_chart(table):
    '''
    Returns the latest chart in the list_of_tuples format that sqlite3 spits out
    '''
    query = f'select * from daily_{table} ORDER BY id DESC LIMIT 10;'
    results = query_db(query)
    return results


class DB_Table:
    database = 'my_spotipy.db'
    tables = ['daily_tracks','daily_artists','recently_played','artist_catalog']
    table_schemas = {
            'artist_catalog' : [
                ('art_id', 'TEXT'),
                ('art_name', 'TEXT'),
                ('followers', 'INTEGER'),
                ('genre', 'TEXT'),
                ('first_release', 'TEXT'),
                ('first_appearance', 'datetime'),
                ('img_url', 'TEXT'),
                ('master_genre', 'TEXT')],
            'daily_tracks' :[('position', 'INTEGER'),
                ('art_id', 'TEXT'),
                ('art_name', 'TEXT'),
                ('album_name', 'TEXT'),
                ('song_id', 'TEXT'),
                ('song_name', 'TEXT'),
                ('date', 'datetime'),],
            'daily_artists':[('position', 'INTEGER'),
                ('art_id', 'TEXT'),
                ('art_name', 'TEXT'),
                ('date', 'datetime'),],
            'recently_played':[('art_name', 'TEXT'),
                ('song_name', 'TEXT'),
                ('song_link', 'TEXT'),
                ('image', 'TEXT'),
                ('last_played', 'TEXT'),]}

    def __init__(self, table):
        self.table = table
        self.schema = self.table_schemas[table]
        self.col_names = [i[0] for i in self.schema]
        self.d_types = [i[1] for i in self.schema]
        

class Daily_Table(DB_Table):
    def __init__(self, table):
        super().__init__(table)
        self.latest_date = query_db(f'select MAX(date) from {self.table}')[0][0]

    def traffic_check(self, new_daily):
        '''
        Uses the tuple that comes from parse_daily_JSON, but with the * to unpack it
        '''
        if self.latest_date < new_daily[0]['date']:
            return True

    def flatten_daily_to_list(self, new_daily):
        '''
        Converts the dictionary into a list of lists. 
        Each list has same length. 
        Each list is a 'column' each index is a 'row'
        '''
        list_version = [list(i.values()) for i in new_daily]
        return list_version


    def insert_new_daily(self, new_daily):
        '''
        the new_daily should be a Spotifies.daily_insert.daily_book
        '''
        #new_date = new_daily[0]['date']
        sql = make_insert_query(self.table, self.col_names)

        if self.traffic_check(new_daily):
            sqliteConnection = sqlite3.connect(self.database)
            cursor = sqliteConnection.cursor()
            #executemany takes a lists of lists, not the usualy dictionary of lists
            flat_daily = self.flatten_daily_to_list(new_daily)
            cursor.executemany(sql, flat_daily)
                
            sqliteConnection.commit()
            cursor.close()
            sqliteConnection.close()

        else:
            print('Failed Traffic Stop')

        print(f'{self.table} has been updated to {self.latest_date}')


class Artist_Catalog(DB_Table):
    def __init__(self, table='artist_catalog'):
        super().__init__(table)
        self.art_cat = query_db('select * from artist_catalog;')
        self.art_ids = [i[0] for i in query_db('SELECT DISTINCT art_id FROM artist_catalog;')]
        self.artists = [i[0] for i in query_db('SELECT DISTINCT art_name FROM artist_catalog;')]

    def first_appearances_in_dailys(self, chart):
        '''
        Finds the first appearance of every art ID in each daily table
        chart should be 'daily_tracks' or 'daily_artists'
        '''
        query = f"select min(date),art_id from {chart} group by art_id;"
        appearances = query_db(query)
        return appearances

    def real_first_appearances(self):
        '''
        Finds first appearance in each daily table, combines them and keeps the earlier record.
        Returns a list of 2-element lists. 0 is the first appearance, 1 is the art_id
        '''
        tracks = self.first_appearances_in_dailys('daily_tracks')
        tracks = [list(i) for i in tracks]
        artists = self.first_appearances_in_dailys('daily_artists')
        artists = [list(i) for i in artists]

        #loop makes sure the earliest date possible is used between the two tables
        for track_pair in tracks:
            for arts_pair in artists: 
                if track_pair[1] == arts_pair[1]:
                    if track_pair[0] > arts_pair[0]:
                        track_pair[0] = arts_pair[0]

        # this brings in the tracks that are only in artists
        tracks_ids = [i[1] for i in tracks]
        ids_only_in_arts = [i for i in artists if i[1] not in tracks_ids]
        tracks.extend(ids_only_in_arts)
        return tracks

    def find_first_appearance(self, art_id):
        '''
        Looks in the old spotify table for a first appearance
        Returns a date. 
        Returns nothing if the art_id is not in real_first_appearances
        '''
        db_firsts = self.real_first_appearances()
        date = [i[0] for i in db_firsts if i[1] == art_id]
        if len(date) > 0:
            return date[0]
    
    def check_in_back(self, art_ids):
        '''
        Returns the art_ids that are not found in the artist catalog
        Returns an empty list if there are no new art ids
        '''
        return [i for i in art_ids if i not in self.art_ids]

    def new_entry(self, art_id):
        '''
        Returns a dictionary that has all the necessary fields to be an entry in the artist catalog
        Makes a Spotify API each time. 
        '''
        my_spobj = new_artist_info(art_id)

        today_date = date.today()
        today_string = today_date.strftime('%Y-%m-%d')

        if self.find_first_appearance(art_id):
            my_spobj.first_appearance = self.find_first_appearance(art_id)
        else:
            my_spobj.first_appearance = today_string

        #my_spobj.first_appearance = self.find_first_appearance(art_id)
        my_spobj.master_genre = assign_master_genre(my_spobj.genre)
        return my_spobj

    def add_to_catalog(self, art_id):
        '''
        Given one art_id, fills out the other 7 necessary fields
        for an artist catalog entry.
        Entry is saved to database.
        '''
        query = make_insert_query(self.table, self.col_names)
        new = self.new_entry(art_id)
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        #executemany takes a lists of lists, not the usualy dictionary of lists

        flat_list = [
            new.art_id,
            new.art_name,
            new.followers,
            new.genre,
            new.first_release,
            new.first_appearance,
            new.img_url,
            new.master_genre
        ]

        cursor.execute(query, flat_list)
        conn.commit()
        cursor.close()
        conn.close()

    def add_new_arts_from_daily(self, art_id_list):
        '''
        Uses *args to work with multiple new artists in one chart. IF there is only one new artists, then
        it will take a list with only one element.
        '''
        for i in art_id_list:
            self.add_to_catalog(i)
        
