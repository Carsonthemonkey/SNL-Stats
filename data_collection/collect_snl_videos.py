import os
import requests
import json
from dotenv import load_dotenv

load_dotenv() # load .env file

API_KEY = os.getenv("YOUTUBE_API_KEY") # Get api key
assert API_KEY is not None

def get_all_channel_video_ids(username):
    playlist_id = get_uploads_playlist(username) # SNL's will be UUqFzWxSCi39LnW1JKFR3efg
    data = get_video_data(playlist_id)
    return get_video_id_list(data)


def get_uploads_playlist(username):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&forUsername={username}&key={API_KEY}"

    # call the api with a timeout of 15 seconds
    response = requests.get(url, timeout=15)

    # convert the json response to a python dictionary
    data = response.json()
    assert isinstance(data, dict)

    print(json.dumps(data, indent=4))
    print(data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"])
    return data

def get_video_data(playlist_id):
    url = f"https://www.googleapis.com/youtube/v3/playlistItems"

    query_params = {
        "key": API_KEY,
        "playlistId": "UUqFzWxSCi39LnW1JKFR3efg", # should be UUqFzWxSCi39LnW1JKFR3efg for SNL
        "part": "snippet",
        "maxResults": 50 # TODO: probably want to use nextPageToken to get all videos
    }

    # call the api with a timeout of 15 seconds
    response = requests.get(url, params=query_params, timeout=15)

    # convert the json response to a python dictionary
    data = response.json()
    assert isinstance(data, dict)

    print(json.dumps(data, indent=4))
    return data

def get_video_id_list(data):
    print(type(data))
    assert isinstance(data, dict)
    ids = [d["snippet"]["resourceId"]["videoId"] for d in data["items"]]
    return ids

if __name__ == "__main__":
    ids = get_all_channel_video_ids("SaturdayNightLive")
    print(len(ids), ids)