import os
import requests
import json
from dotenv import load_dotenv
from pydantic import BaseModel

class Video(BaseModel):
    video_id: str
    title: str
    duration: str
    view_count: int
    like_count: int
    comment_count: int

# Example validation
def get_video_data(video_id):
    data = call_api(video_id)
    video_data = parse_data(data)
    return video_data

def call_api(VIDEO_ID):
    # This is using HTTPS request rather than the python wrapper for the API for now. 
    # The python library seems overcomplicated to me, but we may need it down the line
    load_dotenv() # load .env file

    API_KEY = os.getenv("YOUTUBE_API_KEY") # Get api key
    assert API_KEY is not None

    # start of URL
    url = f"https://www.googleapis.com/youtube/v3/videos"

    # encode the url with the data we want
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
    return data

def parse_data(data):
    assert isinstance(data, dict)

    v = Video(
        video_id=data["items"][0]["id"],
        title=data["items"][0]["snippet"]["title"],
        duration=data["items"][0]["contentDetails"]["duration"],
        view_count=data["items"][0]["statistics"]["viewCount"],
        like_count=data["items"][0]["statistics"]["likeCount"],
        comment_count=data["items"][0]["statistics"]["commentCount"]
    )
    return v

if __name__ == "__main__":
    get_video_data()