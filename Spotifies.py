import spotipy
from config import username, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime



'''
class position_row:
    def __init__(self, table_name, position, spot_dic):
        if table_name == 'daily_artists':
            self.position = position
            self.art_id = spot_dic['id']
            self.art_name = spot_dic['name']
            self.date = datetime.now().strftime("%Y-%m-%d")
        else:
'''            

class request:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        username=username,
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI))

    def __init__(self):
        self.blah = 'blah blah'

    def get_artist_info(self, art_id):             
        '''
        Processes one art_id at a time
        Returns a dictionary. Keys are the columns in artist table. Only one value per key. 

        '''
        artist = self.sp.artist(art_id)
        albums = self.sp.artist_albums(art_id)

        art_name = artist['name']
        followers = artist['followers']['total']
        if len(artist['genres']) == 0:
            genre = 'None'
        else:
            genre = artist['genres'][0]
        
        
        #album_count = len(album_object['items'])
        first_release = min([i['release_date'] for i in albums['items']])
        
        '''
        if self.find_first_appearance(art_id):
            first_appearance = self.find_first_appearance(art_id)
        else:
            first_appearance = datetime.now().strftime("%Y-%m-%d")
        '''

        #I should add a default jpeg in the templating language that is used when the img_url == 'no_image'
        if artist['images']:
            img_url = artist['images'][0]['url']
        else:
            img_url = 'no_image'
        #master_genre = Genres.Genres().new_artist_master_genre(genre)
        #needs master_genre and first_appearance
        new_artist_values = [art_id, art_name, followers, genre, first_release, img_url]
        return new_artist_values

class daily_table(request):
    def __init__(self, table_name):
        super().__init__()
        self.table_name = table_name
        if self.table_name == 'daily_artists':
            self.raw_json = self.sp.current_user_top_artists(time_range='short_term', limit=10)
        else:
            self.raw_json = self.sp.current_user_top_tracks(time_range='short_term', limit=10)

    def JSON_to_listofDicts(self, raw_JSON):
        '''
        Parses a JSON that is delivered from either of the two daily type API requests made
        Use *(table_name, raw_JSON) to unpack the tuple from spot_funcs.daily_table
        '''
        hit_list = []
        position = 1

        if self.table_name == 'daily_artists':

            for i in raw_JSON['items']:
                hit_record = {}
                hit_record['position'] = position
                hit_record['art_id'] = i['id']
                hit_record['art_name'] = i['name']
                hit_record['date'] = datetime.now().strftime("%Y-%m-%d")
                
                position += 1
                hit_list.append(hit_record)
        
        if self.table_name == 'daily_tracks':

            for i in raw_JSON['items']:
                hit_record = {}
                hit_record['position'] = position
                hit_record['art_id'] = i['artists'][0]['id']
                hit_record['art_name'] = i['artists'][0]['name']
                hit_record['album_name'] = i['album']['name']
                hit_record['song_id'] = i['external_urls']['spotify'][-22:]
                hit_record['song_name'] = i['name']
                hit_record['date'] = datetime.now().strftime("%Y-%m-%d")
        
                position += 1
                hit_list.append(hit_record)

        return hit_list
   
class daily_insert(daily_table):
    def __init__(self, table_name):
        super().__init__(table_name)
        self.daily_book = self.JSON_to_listofDicts(self.raw_json)

    #END OF DAILY STUFF#
    ####################


class new_artist_info(request):
    '''
    Accepts an art_id, returns an artist_info object almsot ready for art_cat entry
    It would still require the first_appearance and master_genre attribute assignment.
    '''
    def __init__(self, art_id):
        super().__init__()
        self.art_id = art_id
        self.values = self.get_artist_info(self.art_id)
        self.art_name = self.values[1]
        self.followers = self.values[2]
        self.genre = self.values[3]
        self.first_release = self.values[4]
        self.img_url = self.values[5]
    

class most_recent_song(request):
    '''
    Grabs whatever I was just listening to from the API
    '''
    def __init__(self, table_name='recently_played'):
        super().__init__()
        self.raw_json = self.sp.current_user_recently_played(limit=1)

    def most_recent_dict(self):
        last_song = self.raw_json['items'][0]
        artist_name = last_song['track']['artists'][0]['name']
        song_name =  last_song['track']['name']
        song_link = last_song['track']['external_urls']['spotify']
        image = last_song['track']['album']['images'][0]['url']
        last_played = last_song['played_at']
        return dict(art_name=artist_name, song_name=song_name, song_link=song_link, image=image, last_played=last_played)
        