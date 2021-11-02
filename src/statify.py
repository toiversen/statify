from pandas.core.frame import DataFrame
import requests
import pandas as pd
import streamlit as st
import numpy as np
    
st.set_page_config(layout='wide')

CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]

AUTH_URL = 'https://accounts.spotify.com/api/token'

@st.cache(ttl=3540)
def get_token(id, secret, auth_url):
    # POST
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': id,
        'client_secret': secret
    })

    # convert response to JSON
    auth_response_data = auth_response.json()

    # save the access token
    access_token = auth_response_data['access_token']

    # set request headers
    req_headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }
    return req_headers

req_headers = get_token(CLIENT_ID, CLIENT_SECRET, AUTH_URL)

@st.cache(ttl=3600, allow_output_mutation=True)
def grab_data(req_headers) -> DataFrame:
    '''
    Grab data from Spotify API
    '''
    # hold track info
    data = []

    BASE_URL = 'https://api.spotify.com/v1/' # api base url
    artist_id = '5Wh3G01Xfxn2zzEZNpuYHH' #BAND-MAID

    # pull all albums
    r = requests.get(BASE_URL + 'artists/' + artist_id + '/albums',
            headers=req_headers,
            params={'include_groups': 'album', 'limit': 50})

    # process data dump
    dump = r.json()
    for album in dump['items']:
        if 'JP' in album['available_markets']: # only get the japanese releases
            album_name = album['name']
            # get the tracks from the album
            r_a = requests.get(BASE_URL + 'albums/' + album['id'] + '/tracks', headers=req_headers)
            tracks = r_a.json()
            for track in tracks['items']:
                f = requests.get(BASE_URL + 'audio-features/' + track['id'], headers=req_headers)
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

    # housekeeping
    df['release_date'] = pd.to_datetime(df['release_date'])
    df.drop(columns=['type', 'uri', 'track_href', 'analysis_url', 'album_id', 'id'], inplace=True)
    df = df.reindex(columns=['track_name',
                             'album_name',
                             'energy',
                             'danceability',
                             'speechiness',
                             'acousticness',
                             'instrumentalness',
                             'liveness',
                             'valence',
                             'tempo',
                             'key',
                             'mode',
                             'loudness',
                             'time_signature',
                             'duration_ms',
                             'release_date'])
    df.set_index('track_name', inplace=True)

    # return the data frame
    return df    

# Get some data
df = grab_data(req_headers)

# List of albums. Call set to avoid duplicates
album_names = set(df['album_name'].to_numpy(dtype=str))

# List of metrics to look at
metrics = ['energy',
           'danceability',
           'speechiness', 
           'acousticness', 
           'instrumentalness', 
           'liveness', 
           'valence', 
           'tempo',
           'key',
           'mode',
           'loudness',
           'time_signature',
           'duration_ms']


### Streamlit ####

st.title('BAND-MAID vs. Spotify')

st.dataframe(df)

with st.form('album_metrics_form', clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        selected_album = str(st.selectbox('Select an album', options=album_names))
    with col2:
        selected_metric = st.selectbox('Select a metric', options=metrics)
    submitted = st.form_submit_button('OK')
    if submitted:
        st.write(f'Plotting {selected_metric} for {selected_album}')
        df2 = df[(df['album_name'] == selected_album)][selected_metric]
        st.line_chart(df2, height=500)