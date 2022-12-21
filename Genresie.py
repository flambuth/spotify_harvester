import sqlite3
import json
import os
import pandas as pd

class Genres:
    master_dict = {
    'electronic' : ['electronic','house','techno','dub','chill','bass','beat', 
    'electro', 'clubbing', 'edm', 'club', 'ethnotronica','dnb','dubstep', 'downtempo', 
    'aussietronica','jungle', 'uk_garage', 'breaks'],
    
    'pop' : ['pop','dance', 'future', 'idol', 'wave', 'synth', 'glithcore','escape room', 'anime score',
    'bmore'],
    
    'country' : ['country','bakersfield','tejano', 'rockabilly', 'stomp and holler', 'grass'],
    
    'hip-hop' : ['hip','hop','r&b','rap', 'funk', 'afrofuturism', 'bounce', 'afrobeat', 'brostep',
    'bboy','turntabilism','reggae'],
    
    'punk' : ['punk', 'crack rock steady', 'riot', 'psychobilly', 'ska'],
    
    'indie' : ['indie','emo', 'bubblegrunge','psychedelic'] ,
    
    'rock' : ['rock','metal', 'garage', 'invasion', 'surf', 'grunge', 'aggrotech'], #crack rock steady, 
    
    'old' : ['adult','bossa', 'classical', 'jazz', 'salsa', 'folk', 'vintage', 'early', 
    'classic', 'exotica', 'blues','bebop', 'hammond organ', 'bolero', 'tradicional', 'easy listening',
    'grupera','big band','chanson', 'boogaloo']
    }

    def __init__(self):
        self.blimey = 'maybe my classes are just collections of functions'
        #I suppose this is a relic as long as I keep the JSON around
        #Maybe it'll be useful when I break this up into master functions taht would get imported 
        #by main and a sublcass for doing Genre update/cleanup stuff on its own.

    def distinct_genres_in_db(self):
        '''
        Retruns a list of the genres in the Artists table. Can be several words.
        '''
        conn = sqlite3.Connection('spotify.db')
        cursor = conn.cursor()
        query = 'select distinct genre from artists;'
        blob = cursor.execute(query)
        genres = blob.fetchall()
        return [i[0] for i in genres]

    def genres_with_THIS_word(self, word):
        '''
        Returns a list of genres that use the word given in the parameter.
        Will find the word inside of other words:
            ex ('rock') returns 'blues rock', 'crack rock steady', and 'neo-rockabilly'
                ('fi') return ['lo-fi house', 'lo-fi indie', 'bakersfield sound']
        '''
        generos = self.distinct_genres_in_db()
        return sorted([i for i in generos if word in i])

    def write_genres_to_json(self, genre_book):
        '''
        Saves the dictionary harvested from the old_artist table into a json
        Will write whatever dictionary you give it.
        Use genre_assignment as the input
        '''

        a_file = open('genres.json', "w")
        json.dump(genre_book, a_file)
        a_file.close()

    def genre_book(self):
        '''
        Return the dictionary of the master_genre:genre assignments from the JSON
        '''
        if os.path.exists('genres.json'):
            with open('genres.json', 'r') as myfile:
                data=myfile.read()
            genre_book = json.loads(data)
        
        else:
            genre_book = self.genre_assignment()
            self.write_genres_to_json(genre_book)
        
        return genre_book

    def add_genre_to_json(self, new_genre, master_genre):
        '''
        Function to explicility direct the master_genre that will have a new genre appended to it's list
        '''
        genre_json = open('genres.json', "w")
        genre_book = json.loads(genre_json)
        genre_book[master_genre].append(new_genre)
        self.write_genres_to_json(genre_book)

    def find_word_in_dicts(self, word):
        '''
        Function to see if the input word ISIN the lists that are the values in the genre_dicts()
        Returns a true or false
        '''
        genre_simple = self.master_dict

        matches = [i for i in genre_simple if word in genre_simple[i]]
        if len(matches) > 0:
            return matches[0]
        else:
            return 'No Match'


    def new_genre_encounter(self, new_genre):
        '''
        Used when an explicit match for evaluating a genre could not be found
        Breaks the input word into grams. If one of them is in the monograms used in the master_dicts,
        it gets the master_genre that uses that monogram
        '''
        grams = new_genre.split(' ')
        blob = [self.find_word_in_dicts(i) for i in grams if self.find_word_in_dicts(i) != 'No Match']
        if blob:
            #turn this one when we can confirm it works - 20july2022
            #self.add_genre_to_json(new_genre, blob[0])
            return blob[0]
        else:
            return 'Other'

    def new_artist_master_genre(self, new_artist_genre):
        '''
        Function used when evaluating a new entry to the artist table
        First looks for an explicit string match. Then it tries a function for encountering new genres
        '''
        book = self.genre_book()
        listcomp = [i for i in book if new_artist_genre in book[i]]

        if len(listcomp) > 0:
            return listcomp[0]
        else:
            return self.new_genre_encounter(new_artist_genre)


class Genre_Update(Genres):
    def find_genre_match(self, test_word):
        '''
        Loops through the master_genre : key words, in the order they are written at the top of this
        thing. It breaks out of the function on the first match, so that order matters.
        '''
        keyword_dict = self.master_dict
        for master_genre in keyword_dict.keys():
            for key_word in keyword_dict[master_genre]:
                if key_word in test_word:
                    return master_genre
        return 'Other'

    def pair_master_with_genres(self):
        '''
        Applys the find_genre_match function to each distinct_genre
        254 distinct genres on 
        '''
        all_the_genres = self.distinct_genres_in_db()
        return [(self.find_genre_match(i),i) for i in all_the_genres]

    def genre_assignment(self):
        '''
        Using the current master_genre:genre dictionary/JSON, assigns a master_genre 
        '''
        genre_assignments = {
        'electronic' : [],
        'pop' : [],
        'country' : [],
        'hip-hop' : [],
        'punk' : [],
        'indie' : [] ,
        'rock' : [], #crack rock steady, 
        'old' : [],
        'Other' : []
        }
        
        [genre_assignments[i[0]].append(i[1]) for i in self.pair_master_with_genres()]

        for i in genre_assignments.keys():
            genre_assignments[i].sort()
        return genre_assignments

    def update_genre_df(self):
        old_cols = ['genre','art_id']
        old_df = pd.DataFrame(self.distinct_arts(),columns=old_cols)
        
        new_cols = ['master_genre','genre']
        new_df = pd.DataFrame(self.pair_master_with_genres(),columns=new_cols)
        
        pandas_df = old_df.merge(new_df, on='genre')
        return pandas_df

    def update_genre_sqlite(self):
        '''
        Joins the new master_genre tags with the art_ids in the database,
        bulk UPDATEs the artist2 table with the new tags
        '''
        sql = ''' UPDATE artists2
              SET master_genre = ? 
              WHERE art_id = ?'''
        process_this = self.update_genre_df()[['master_genre','art_id']].to_records(index=False)

              
        sqliteConnection = sqlite3.connect('spotify.db')
        cursor = sqliteConnection.cursor()
        
        cursor.executemany(sql, process_this)

        sqliteConnection.commit()
        cursor.close()
        sqliteConnection.close()


#Functions that take that use those objects. I think the only time this library is 
# used is for the new artist catalog entry function    
def assign_master_genre(genre):
    this_thing = Genres().new_artist_master_genre(genre)
    return this_thing


