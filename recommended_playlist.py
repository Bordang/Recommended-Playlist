from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv('my.env')
cid = os.getenv('SPOTIPY_CLIENT_ID')
secret = os.getenv('SPOTIPY_CLIENT_SECRET')
redirect = os.getenv('SPOTIPY_REDIRECT_URI')
scope = "playlist-modify-private playlist-modify-public user-top-read user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cid,
                                               client_secret=secret,
                                               redirect_uri=redirect,
                                               scope=scope,
                                               open_browser=False))

def top_genres(top_artists):
    genres = []
    for item in top_artists['items']:
        for genre in item['genres']:
            if genre not in genres:
                genres.append(genre)
    return genres

def pull_uri_from_tracks(tracks):
    track_uris = []
    for item in tracks['items']:
        track_uri = item['track']['uri']
        track_uris.append(track_uri)
    return track_uris

def pull_artists_from_tracks(tracks):
    artists = []
    for item in tracks['items']:
        for artist in item['track']['artist']:
            if artist not in artists:
                artists.append(artist)
    return artists

def list_top_artists(top_artists):
    return [artist['name'] for artist in top_artists['items']]

def is_track_in_playlist(playlist_uri, track_uri):
    playlist_tracks = sp.playlist_tracks(playlist_uri)
    for item in playlist_tracks['items']:
        if item['track']['uri'] == track_uri:
            return True
    return False

#Filters tracks into playlist based on genres provided
def filter_to_playlist(playlist_id, playlist_uri, genres, tracks): 
    count = 0
    filtered_songs = []
    for item in tracks:
        count += 1
        print("Progress: " + str(count) + " out of " + str(len(tracks)) + " tracks vetted this cycle")
        #if is_track_in_playlist(playlist_uri, item['track']['uri']):
            #continue
        track_added = False
        for a in item['track']['artists']:
            if track_added:
                print("Track is already in playlist")
                break
            artist = sp.artist(a['uri'])
            for genre in artist['genres']:
                if track_added:
                    break
                if genre in genres:
                    print("Track added")
                    track_added = True
                    #sp.playlist_add_items(playlist_id=playlist_id, items=[item['track']['uri']])
                    filtered_songs.append(item['track']['uri'])
                    break
        if not track_added:
            print("Track not added")
    return filtered_songs
            
try:
    print("How many genres do you want to include? Type only the number followed by pressing \'Enter\'")
    NUM_GENRES = int(input())  
    current_user = sp.current_user()
    username = current_user['id']
    top_artists_dict = sp.current_user_top_artists(time_range='short_term')
    #top_artists = list_top_artists(top_artists_dict)                                                                                #List of top artists names
    genres = top_genres(top_artists_dict)                                                                                           #List of names of genres
    print("Here are your top generes:")
    print(genres)
    print(f"Input {NUM_GENRES} genres you would like to filter for. Type them one at a time exactly as they are shown in Spotify genre documentation (https://gist.github.com/andytlr/4104c667a62d8145aa3a) followed by pressing \'Enter\':")
    new_genres = []
    for i in range(NUM_GENRES):
        new_genres.append(input())
    description = "Generated by Bordang's Recommended Playlist Script. Genres: " + ", ".join(new_genres)
    print("Creating playlist...")
    playlist = sp.user_playlist_create(user=username,name="Your Recommended Playlist (In Progress)",description=description)
    print("Playlist created")
    current_tracks = sp.current_user_saved_tracks(limit=50)
    tracks = []
    tracks.append(current_tracks['items'])
    print("Getting saved songs in Liked Songs")
    for i in range(20):
        current_tracks = sp.next(current_tracks)
        tracks.append(current_tracks['items'])
    count = 1
    print("List of songs generated")
    print("Filtering starting:")
    for some_tracks in tracks:
        print(f"Loop {count} of 20")
        count += 1
        filtered_songs = filter_to_playlist(playlist['id'], playlist['uri'], new_genres, some_tracks)
        if len(filtered_songs) > 0:
            sp.playlist_add_items(playlist_id=playlist['id'], items=filtered_songs)
    sp.user_playlist_change_details(user='me',playlist_id=playlist['id'],name="Your Recommended Playlist")
except spotipy.SpotifyException as e: 
        print(e)