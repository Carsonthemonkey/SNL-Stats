import os
import requests
import asyncio
import aiohttp
from tqdm import tqdm
from dotenv import load_dotenv
from schema import Video

load_dotenv()  # load .env file
API_KEY = os.getenv("YOUTUBE_API_KEY")  # Get api key
if API_KEY is None: 
    raise KeyError("API key not found in .env file")


def fetch_video_statistics(video_ids: list) -> list:
    # max number of videos per request is 50, so we need to do it in batches
    video_data = []
    pbar = tqdm(total=len(video_ids), desc="Fetching video statistics")
    while len(video_ids) > 0:
        pbar.update(50)
        video_data.extend(_fetch_videos(video_ids[:50]))
        video_ids = video_ids[50:]
    
    pbar.close()

    video_data = [_extract_video_statistics(video) for video in video_data]
    return video_data


async def fetch_video_comments(
    video_id: str,
    comment_number: int,
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
) -> list:
    comments_endpoint = "https://www.googleapis.com/youtube/v3/commentThreads"
    query_params = {
        "key": API_KEY,
        "videoId": video_id,
        "maxResults": comment_number,
        "part": "snippet,replies",
    }
    try:
        async with semaphore:
            async with session.get(
                comments_endpoint, params=query_params, timeout=15
            ) as res:
                comment_data = await res.json()
                comments = [
                    comment["snippet"]["topLevelComment"]["snippet"]["textOriginal"]
                    for comment in comment_data["items"]
                ]
                while comment_data.get("nextPageToken"):
                    query_params["pageToken"] = comment_data["nextPageToken"]
                    async with session.get(
                        comments_endpoint, params=query_params, timeout=15
                    ) as res:
                        comment_data = await res.json()
                        comments.extend(
                            [
                                comment["snippet"]["topLevelComment"]["snippet"][
                                    "textOriginal"
                                ]
                                for comment in comment_data["items"]
                            ]
                        )
                return comments
    except TimeoutError:
        print(f"Timeout Error for video ID: {video_id}")


def fetch_all_channel_videos(username: str) -> list:
    playlist_id = _fetch_uploads_playlist_id(
        username
    )  # SNL's will be UUqFzWxSCi39LnW1JKFR3efg
    data = _fetch_channel_videos(playlist_id)
    return _extract_video_info(data)

def _fetch_uploads_playlist_id(username: str) -> str:
    url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&forUsername={username}&key={API_KEY}"

    # call the api with a timeout of 15 seconds
    response = requests.get(url, timeout=15)

    # convert the json response to a python dictionary
    data = response.json()
    assert isinstance(data, dict)

    return data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

def _fetch_channel_videos(playlist_id):
    url = f"https://www.googleapis.com/youtube/v3/playlistItems"

    query_params = {
        "key": API_KEY,
        "playlistId": playlist_id,
        "part": "snippet",
        "maxResults": 50,
    }

    # call the api with a timeout of 15 seconds
    response = requests.get(url, params=query_params, timeout=15)

    # convert the json response to a python dictionary
    data_res = response.json()
    data = data_res["items"]
    assert isinstance(data, list)

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

def _fetch_videos(video_ids: list) -> dict:
    videos_endpoint = f"https://www.googleapis.com/youtube/v3/videos"
    assert len(video_ids) <= 50, "Max number of videos per request is 50"
    # encode the url with the data we want
    query_params = {
        "key": API_KEY,
        "id": video_ids[:50],
        "part": "statistics,snippet,contentDetails",
    }

    # call the api with a timeout of 15 seconds
    response = requests.get(videos_endpoint, params=query_params, timeout=15).json()
    try:
        video_stats = response["items"]
    except KeyError:
        print(response)
        raise KeyError("No videos found for given ids")
    while response.get("nextPageToken"):
        response = requests.get(videos_endpoint, params=query_params, timeout=15).json()
        response = response.json()
        query_params["pageId"] = response["nextPageToken"]
        response = requests.get(videos_endpoint, params=query_params, timeout=15)
        video_stats.extend(response.json()["items"])

    return video_stats

def _extract_video_statistics(data: dict) -> dict:
    assert isinstance(data, dict)
    # data = data["items"][0]
    # v = Video(
    #     video_id=data["id"],
    #     title=data["snippet"]["title"],
    #     duration=data["contentDetails"]["duration"],
    #     view_count=data["statistics"]["viewCount"],
    #     like_count=data["statistics"]["likeCount"],
    #     comment_count=data["statistics"]["commentCount"]
    # )
    v = {
        "video_id": data["id"],
        "title": data["snippet"]["title"],
        "duration": data["contentDetails"]["duration"],
        "view_count": int(data["statistics"]["viewCount"]),
        "like_count": int(data["statistics"]["likeCount"]),
        "comment_count": int(data["statistics"]["commentCount"]),
        "upload_date": data["snippet"]["publishedAt"]
    }
    return v

def _extract_video_info(videos):
    video_data = [
        {
            "id": video["snippet"]["resourceId"]["videoId"],
            "title": video["snippet"]["title"],
        }
        for video in videos
    ]
    return video_data


async def main():
    # session = aiohttp.ClientSession()
    # semaphore = asyncio.Semaphore(15)
    videos = fetch_video_statistics(["dQw4w9WgXcQ", "P-MrIIEIPek"])
    for video in videos:
        print(video)
    # await session.close()


if __name__ == "__main__":
    asyncio.run(main())
