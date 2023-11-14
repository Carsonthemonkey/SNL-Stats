import os
import requests
import json
from dotenv import load_dotenv

def main():
    load_dotenv() # load .env file

    API_KEY = os.getenv("YOUTUBE_API_KEY") # Get api key
    assert API_KEY is not None

    # start of URL
    url = f"https://www.googleapis.com/youtube/v3/playlistItems"
    # "UCqFzWxSCi39LnW1JKFR3efg" # SNL channel id
    # uploads playlist id: UUqFzWxSCi39LnW1JKFR3efg

    query_params = {
        "key": API_KEY,
        "playlistId": "UUqFzWxSCi39LnW1JKFR3efg",
        "part": "snippet"
        # maxResults=50
    }

    # call the api with a timeout of 15 seconds
    response = requests.get(url, params=query_params, timeout=15)

    # convert the json response to a python dictionary
    data = response.json()
    assert isinstance(data, dict)

    print(json.dumps(data, indent=4))
    return data

if __name__ == "__main__":
    main()