import os
import requests
import asyncio
import aiohttp
from dotenv import load_dotenv
from schema import Video

load_dotenv()  # load .env file
API_KEY = os.getenv("YOUTUBE_API_KEY")  # Get api key
assert API_KEY is not None


def fetch_video_statistics(video_ids: list) -> list:
    video_data = _fetch_videos(video_ids)
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

def _fetch_videos(video_ids: list) -> dict:
    videos_endpoint = f"https://www.googleapis.com/youtube/v3/videos"

    # encode the url with the data we want
    query_params = {
        "key": API_KEY,
        "id": video_ids,
        "part": "statistics,snippet,contentDetails",
    }

    # call the api with a timeout of 15 seconds
    response = requests.get(videos_endpoint, params=query_params, timeout=15).json()
    video_stats = response["items"]
    while response.get("nextPageToken"):
        response = requests.get(videos_endpoint, params=query_params, timeout=15).json()
        response = response.json()
        query_params["pageId"] = response["nextPageToken"]
        response = requests.get(videos_endpoint, params=query_params, timeout=15)
        video_stats.extend(response.json()["items"])

    return video_stats

def _extract_video_statistics(data: dict) -> Video:
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
        "view_count": data["statistics"]["viewCount"],
        "like_count": data["statistics"]["likeCount"],
        "comment_count": data["statistics"]["commentCount"],
    }
    return v


async def main():

    # session = aiohttp.ClientSession()
    # semaphore = asyncio.Semaphore(15)
    videos = fetch_video_statistics(["dQw4w9WgXcQ", "P-MrIIEIPek"])
    for video in videos:
        print(video)
    # await session.close()


if __name__ == "__main__":
    asyncio.run(main())
