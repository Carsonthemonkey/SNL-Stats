import os
import requests
import json
from dotenv import load_dotenv

# This is using HTTPS request rather than the python wrapper for the API for now. The python library seems overcomplicated to me, but we may need it down the line

load_dotenv() # load .env file

API_KEY = os.getenv("YOUTUBE_API_KEY") # Get api key
assert API_KEY is not None
VIDEO_ID = "dQw4w9WgXcQ" 

# encode the URL with the data we want
url = f"https://www.googleapis.com/youtube/v3/videos"

query_params = {
    "key": API_KEY,
    "id": VIDEO_ID,
    "part": "statistics,snippet,contentDetails"
}

# call the api with a timeout of 15 seconds
response = requests.get(url, params=query_params, timeout=15)

# convert the json response to a python dictionary
data = response.json()
assert isinstance(data, dict)

print(json.dumps(data, indent=4))