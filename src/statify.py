import os
from dotenv import load_dotenv
from pandas.core.frame import DataFrame
import requests
import pandas as pd

def grab_access_token():
    '''
    Request new access token from Spotify Auth
    '''
    load_dotenv()
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')

    AUTH_URL = 'https://accounts.spotify.com/api/token'

    # POST
    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })

    # convert response to JSON
    auth_response_data = auth_response.json()

    # save the access token
    access_token = auth_response_data['access_token']
    return access_token


def grab_data(access_token: str) -> DataFrame:
    '''
    Grab data from Spotify API
    '''
    # hold track info
    data = []

    # set request headers
    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }

    BASE_URL = 'https://api.spotify.com/v1/' # api base url
    artist_id = '5Wh3G01Xfxn2zzEZNpuYHH' #BAND-MAID

    # pull all albums
    r = requests.get(BASE_URL + 'artists/' + artist_id + '/albums',
            headers=headers,
            params={'include_groups': 'album', 'limit': 50})

    # process data dump
    dump = r.json()
    for album in dump['items']:
        if 'JP' in album['available_markets']: # only get the japanese releases
            album_name = album['name']
            # get the tracks from the album
            r_a = requests.get(BASE_URL + 'albums/' + album['id'] + '/tracks', headers=headers)
            tracks = r_a.json()
            for track in tracks['items']:
                f = requests.get(BASE_URL + 'audio-features/' + track['id'], headers=headers)
                f = f.json()
            
            # add some album info
                f.update({
                    'track_name': track['name'],
                    'album_name': album_name,
                    'release_date': album['release_date'],
                    'album_id': album['id']
                })
                data.append(f)
    
    # make a dataframe for the track data
    df = pd.DataFrame(data)

    # proper date format
    df['release_date'] = pd.to_datetime(df['release_date'])
    df.drop(columns=['type', 'uri', 'track_href', 'analysis_url'], inplace=True)

    # return the data frame
    return df    


def main():
    '''
    Entry point
    '''
    access_token = grab_access_token
    df = grab_data(access_token)
    print(df.head())
    df.to_csv('tracks.csv')


if __name__ == "__main__":
    main()