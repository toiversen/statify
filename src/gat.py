### GET ACCESS TOKEN ###

import os, requests
from dotenv import load_dotenv

# Load env variables
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

print(access_token)