from Spotifies import most_recent_song
from Databasies import Recently_Played

def add_song_to_recently_played():
    rp_db = Recently_Played()
    latest_spotify_song = most_recent_song().most_recent_dict()

    if rp_db.latest_song[0][2] == latest_spotify_song['song_name']:
        print('Song is a repeat.')

    else:
        rp_db.add_most_recent_song(latest_spotify_song)

if __name__ == "__main__":
    add_song_to_recently_played()