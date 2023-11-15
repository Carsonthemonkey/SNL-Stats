import argparse
import multiprocessing
import asyncio
import aiohttp
from tqdm.asyncio import tqdm
from tqdm import tqdm as sync_tqdm
from data_collection.snl_archive_scraper import (
    get_all_episode_urls,
    get_scenes_from_episode_url,
)
from data_collection.youtube import fetch_all_channel_videos
from data_collection.fuzzy_search import get_matching_string
from analysis.load_data import (
    load_scene_data,
    load_video_data,
)
import datetime
import json


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scrape-scenes",
        help="fetch up to date scene data instead of relying on stored data",
        action="store_true",
    )
    parser.add_argument(
        "--get-stats",
        help="get all video statistics from the youtube api",
        action="store_true",
    )
    parser.add_argument("--all", "-a", help="re-collect all data", action="store_true")

    args = parser.parse_args()

    # Load or collect scene data
    if args.scrape_scenes or args.all:
        print("Scraping scenes...")
        async with aiohttp.ClientSession() as session:
            urls = await get_all_episode_urls(session)
            print(f"found {len(urls)} episodes")
            pbar = tqdm(total=len(urls), desc="Collecting scene data")

            def on_complete():
                pbar.update(1)

            semaphore = asyncio.Semaphore(15)
            tasks = [
                asyncio.create_task(
                    get_scenes_from_episode_url(url, session, semaphore)
                )
                for url in urls
            ]

            for task in tasks:
                task.add_done_callback(on_complete)

            episodes = await asyncio.gather(*tasks)
        scenes = [
            dict(scene)
            for episode in episodes
            if episode is not None
            for scene in episode
            if scene is not None
        ]

        with open("data/scenes.json", "w", encoding="utf-8") as f:
            data = {
                "last_collected": datetime.datetime.now().isoformat(),
                "scene_data": scenes,
            }
            json.dump(data, f, indent=4)
    else:
        scenes = load_scene_data()

    # Collect or load youtube stats
    if args.get_stats or args.all:
        # collect youtube data
        print("Getting videos from youtube...")
        channel_videos = fetch_all_channel_videos("SaturdayNightLive")

        with open("data/channel_videos.json", "w", encoding="utf-8") as f:
            data = {
                "last_collected": datetime.datetime.now().isoformat(),
                "channel_videos": channel_videos,
            }
            json.dump(data, f, indent=4)
    else:
        # load youtube data
        channel_videos = load_video_data()

    blocked_strings = ["behind the sketch"] # Use this to manually filter titles
    filtered_videos = [
        video
        for video in channel_videos["channel_videos"]
        for blocked in blocked_strings
        if video["title"] is not None and blocked not in video["title"].lower()
    ]
    scene_titles = [
        scene["title"] for scene in scenes["scene_data"] if scene["title"] is not None
    ]
    # match videos based on title
    composite_data = []
    # matching_titles = []
    for video in sync_tqdm(filtered_videos, desc="Indexing video titles"):
        if video['title'] is None:
            pass
        matching_scene_title = get_matching_string(video['title'], scene_titles, 0.9)
        if matching_scene_title is not None:
            matching_scene = get_scene_by_title(matching_scene_title, scenes['scene_data'])
            matched_video = {
                'id': video['id'],
                **matching_scene,
            }
            composite_data.append(matched_video)
            # matching_titles.append(matching_scene_title)

    print(len(composite_data))
    print(composite_data[0])
    # Collect or load comment sentiment

def get_scene_by_title(title: str, scenes: list) -> dict:
    for scene in scenes:
        if scene['title'] == title:
            return scene
        

asyncio.run(main())
