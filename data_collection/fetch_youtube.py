import os
import requests
import asyncio
import aiohttp
from dotenv import load_dotenv
from schema import Video

load_dotenv() # load .env file
API_KEY = os.getenv("YOUTUBE_API_KEY") # Get api key
assert API_KEY is not None

async def get_video_data(video_id: str, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore):
    data = await fetch_video(video_id, session, semaphore)
    video_data = parse_video_statistics(data)
    return video_data

async def fetch_video(video_id: str, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore) -> dict:
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
    async with semaphore:
        async with session.get(url, params=query_params, timeout=15) as response:
            return await response.json()


async def get_video_comments(video_id: str, comment_number: int, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore) -> list:
    comments_endpoint = "https://www.googleapis.com/youtube/v3/commentThreads"
    query_params = {
        "key": API_KEY,
        "videoId": video_id,
        "maxResults": comment_number,
        "part": "snippet,replies"
    }
    try:
        async with semaphore:
            async with session.get(comments_endpoint, params=query_params, timeout=15) as res:       
                comment_data = await res.json()
                comments = [comment['snippet']['topLevelComment']['snippet']['textOriginal'] for comment in comment_data['items']]
                while comment_data.get('nextPageToken'):
                    query_params['pageToken'] = comment_data['nextPageToken']
                    async with session.get(comments_endpoint, params=query_params, timeout=15) as res:
                        comment_data = await res.json()
                        comments.extend([comment['snippet']['topLevelComment']['snippet']['textOriginal'] for comment in comment_data['items']])
                return comments
    except TimeoutError:
        print(f'Timeout Error for video ID: {video_id}')

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

async def main():
    session = aiohttp.ClientSession()
    semaphore = asyncio.Semaphore(15)
    video_stats = await get_video_data("dQw4w9WgXcQ", session, semaphore)
    comments = await get_video_comments("6euomDxdHsY", 2000, session, semaphore)
    print(video_stats)
    for comment in comments:
        print(comment)
    await session.close()


if __name__ == "__main__":
    asyncio.run(main())