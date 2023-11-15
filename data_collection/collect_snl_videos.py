import os
import requests
import json
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()  # load .env file

API_KEY = os.getenv("YOUTUBE_API_KEY")  # Get api key
assert API_KEY is not None


def get_all_channel_video_ids(username):
    playlist_id = get_uploads_playlist(
        username
    )  # SNL's will be UUqFzWxSCi39LnW1JKFR3efg
    data = get_video_data(playlist_id)
    return extract_video_data(data)
    # TODO: also want to return the video titles with the ids


def get_uploads_playlist(username):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&forUsername={username}&key={API_KEY}"

    # call the api with a timeout of 15 seconds
    response = requests.get(url, timeout=15)

    # convert the json response to a python dictionary
    data = response.json()
    assert isinstance(data, dict)

    return data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_video_data(playlist_id):
    url = f"https://www.googleapis.com/youtube/v3/playlistItems"

    query_params = {
        "key": API_KEY,
        "playlistId": playlist_id,  # should be UUqFzWxSCi39LnW1JKFR3efg for SNL
        "part": "snippet",
        "maxResults": 50,
    }

    # call the api with a timeout of 15 seconds
    response = requests.get(url, params=query_params, timeout=15)

    # convert the json response to a python dictionary
    data_res = response.json()
    data = data_res["items"]
    assert isinstance(data, list)

    # TODO: add a progress bar?
    with tqdm(total=None, desc='fetching channel videos', unit=' videos', ncols=100) as pbar:
        last_len = len(data)
        pbar.update(last_len)
        while data_res.get("nextPageToken"):
            query_params["pageToken"] = data_res["nextPageToken"]
            response = requests.get(url, params=query_params, timeout=15)
            data_res = response.json()
            data.extend(data_res["items"])
            pbar.update(len(data) - last_len)
            last_len = len(data)

    # print(json.dumps(data, indent=4))
    return data


def extract_video_data(videos):
    video_data = [
        {
            "id": video["snippet"]["resourceId"]["videoId"],
            "title": video["snippet"]["title"],
        }
        for video in videos
    ]
    return video_data


if __name__ == "__main__":
    ids = get_all_channel_video_ids("SaturdayNightLive")
    print(len(ids), ids)
