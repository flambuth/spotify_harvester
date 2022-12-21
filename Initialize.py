import sqlite3

from django.template import Origin
#from datetime import datetime

#from django.template import Origin
#from spot_funcs import get_artist_info
#from Spotifies import daily_insert
#import Genresie

class Origin_Story:
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
    
    def __init__(self):
        self.woah = 'this whole time I should have been using class variables'

    def make_create_query(self, table_name):
        '''
        Assembles a CREATE TABLE SQL statement. The module 'table_schemas.py' has the column_names and their data types
        saved as list of tuples.

        Assigns a 'id' column as the primary_field

        '''
        header = f'CREATE TABLE {table_name} ( id INTEGER PRIMARY KEY,'
        footer = ');'
        col_tuples = self.table_schemas[table_name]
        #makes a list of rows for each entry from the table_schemas tuples
        list_of_rows = [f'{i[0]} {i[1]} NOT NULL,' for i in col_tuples]
        #drops the last comma. Apparently that really matters to sqlite3
        list_of_rows[-1] = list_of_rows[-1][:-1]
        fields = ' '.join(list_of_rows)

        script = header + fields + footer
        return script
    
    def check_if_table_exists(self, table_name):
        '''
        Returns true if the input string is found in the class database
        '''
        conn = sqlite3.connect('my_spotipy.db')
        c = conn.cursor()
        query = f''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{table_name}' '''
        c.execute(query)

        if c.fetchone()[0]==1 :
            return True
        else:
            return False

    def drop_table(self, table_name):
        conn = sqlite3.connect('my_spotipy.db')
        c = conn.cursor()
        dropTableStatement = f"DROP TABLE {table_name}"
        c.execute(dropTableStatement)

        print(f'{table_name} has been dropped.')

    def create_table(self, table_name):
        '''
        One function that takes one of the tuples in a list over on table_schemas.py
        '''
        #I wonder if decoraters would be the apropriate way to do the open and close connection to 
        # the sqlite3 db
        if self.check_if_table_exists(table_name):   
            self.drop_table(table_name)

        try:
            sqliteConnection = sqlite3.connect(self.database)
            sqlite_create_table_query = self.make_create_query(table_name)
        
            cursor = sqliteConnection.cursor()
            print("Successfully Connected to SQLite")
            cursor.execute(sqlite_create_table_query)
            sqliteConnection.commit()
            print(f"{table_name} table created")
        
            cursor.close()
        
        except sqlite3.Error as error:
            print("That table did not create OK. Tough break", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("Making sure you close the door on the way out")
    
    def create_all_tables(self):
        '''  
        Orchestrates the creation of the four tables needed in the database for my_spotipy. Should be run as the 
        first act of this application
        '''
        for i in self.tables:
            self.create_table(i)

    def insert_from_old_db(self, table):
        '''
        
        '''
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        old_db = ('spotify.db',)
        attachSQL = ''' ATTACH DATABASE ? AS old_db; '''

        if table == 'artist_catalog':
            insertSQL = ''' INSERT INTO artist_catalog SELECT * FROM old_db.artists2;'''
        else:
            insertSQL = f''' INSERT INTO {table} SELECT * FROM old_db.{table}; '''
        
        cursor.execute(attachSQL, old_db)

        cursor.execute(insertSQL)
        conn.commit()
        conn.close()

    def initialize(self):
        self.create_all_tables()
        for i in self.tables:
            self.insert_from_old_db(i)
            print(f'created {i}')
        print('Database is ready to go!')

anfisa = Origin_Story()

########################################################
