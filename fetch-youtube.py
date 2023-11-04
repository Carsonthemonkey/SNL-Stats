import os
import requests
import json
from dotenv import load_dotenv
from pydantic import BaseModel

class Video(BaseModel):
    video_id: str
    title: str
    duration: int
    view_count: int
    like_count: int
    comment_count: int

# Example validation
def main():
    get_video_id()
    data = call_api()
    data = convert_to_video_object(parse_data(data))


def get_video_id():
    pass

def call_api():
    # This is using HTTPS request rather than the python wrapper for the API for now. 
    # The python library seems overcomplicated to me, but we may need it down the line
    load_dotenv() # load .env file

    API_KEY = os.getenv("YOUTUBE_API_KEY") # Get api key
    assert API_KEY is not None
    VIDEO_ID = "dQw4w9WgXcQ" 

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
    # v = {
    #     "video_id": "whee",
    #     "title": "hello",
    #     "duration": 6,
    #     "view_count": 6,
    #     "like_count": 6,
    #     "comment_count": 6
    # }
    pass

def convert_to_video_object(v):
    v = Video(**v)
    print(type(v))
    return(v)



if __name__ == "__main__":
    main()