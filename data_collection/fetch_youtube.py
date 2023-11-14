import os
import requests
import json
from dotenv import load_dotenv
from schema import Video

load_dotenv() # load .env file
API_KEY = os.getenv("YOUTUBE_API_KEY") # Get api key
assert API_KEY is not None

def get_video_data(video_id: str):
    data = fetch_video(video_id)
    video_data = parse_video_statistics(data)
    return video_data

def fetch_video(video_id: str) -> dict:
    # This is using HTTPS request rather than the python wrapper for the API for now. 
    # The python library seems overcomplicated to me, but we may need it down the line
    # start of URL
    url = f"https://www.googleapis.com/youtube/v3/videos"

    # encode the url with the data we want
    query_params = {
        "key": API_KEY,
        "id": video_id,
        "part": "statistics,snippet,contentDetails"
    }

    # call the api with a timeout of 15 seconds
    response = requests.get(url, params=query_params, timeout=15)

    # convert the json response to a python dictionary
    return response.json()
    

def parse_video_statistics(data: dict) -> Video:
    assert isinstance(data, dict)
    data = data["items"][0]
    v = Video(
        video_id=data["id"],
        title=data["snippet"]["title"],
        duration=data["contentDetails"]["duration"],
        view_count=data["statistics"]["viewCount"],
        like_count=data["statistics"]["likeCount"],
        comment_count=data["statistics"]["commentCount"]
    )
    return v

if __name__ == "__main__":
    v = get_video_data("dQw4w9WgXcQ")
    print(dict(v))