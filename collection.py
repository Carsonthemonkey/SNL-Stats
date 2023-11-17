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

    # Collect or load titles and ids of all SNL videos
    if args.get_stats or args.all:
        # collect titles and ids of all SNL videos
        print("Getting videos from youtube...")
        channel_videos = fetch_all_channel_videos("SaturdayNightLive")

        with open("data/channel_videos.json", "w", encoding="utf-8") as f:
            data = {
                "last_collected": datetime.datetime.now().isoformat(),
                "channel_videos": channel_videos,
            }
            json.dump(data, f, indent=4)
    else:
        # load titles and ids of all SNL videos
        channel_videos = load_video_data()

    blocked_strings = ["behind the sketch", "behind the scenes", "bloopers", "(live)"] # Use this to manually filter titles
    filtered_videos = [
        video
        for video in channel_videos["channel_videos"]
        if video["title"] is not None and "- SNL" in video["title"] and not any(blocked in video["title"].lower() for blocked in blocked_strings)
    ]

    scene_titles = [
        scene["title"] for scene in scenes["scene_data"] if scene["title"] is not None
    ]

    # TODO: Collect or load youtube stats
    if args.get_stats or args.all:
        # collect youtube data
        pass
    else:
        # load youtube data
        pass

    # match videos based on title
    composite_data = []
    
    # load function args into list of tuples for multiprocessing
    args = [(vid, scene_titles, scenes['scene_data']) for vid in filtered_videos if vid['title'] is not None]
    
    num_processes = multiprocessing.cpu_count()
    print(f'Utilizing {num_processes} CPU cores for title matching')
    with multiprocessing.Pool(processes=num_processes) as pool:
        for result in sync_tqdm(pool.imap_unordered(multi_core_wrapper, args),total=len(args) , desc="Indexing video titles"):
            if result is not None:
                composite_data.append(result)

    print(len(composite_data))
    print(composite_data[0])
    
    # Collect or load comment sentiment

def multi_core_wrapper(args: tuple):
    return get_combined_data_from_video_info(*args)

def get_combined_data_from_video_info(video_info: dict, scene_titles, scene_data: list) -> dict:
    matching_scene_title = get_matching_string(video_info['title'], scene_titles, 0.9)
    if matching_scene_title is not None:
        matching_scene = get_scene_by_title(matching_scene_title, scene_data)
        matched_video = {
            'id': video_info['id'],
            **matching_scene
        }
        return matched_video

def get_scene_by_title(title: str, scenes: list) -> dict:
    for scene in scenes:
        if scene['title'] == title:
            return scene


if __name__ == '__main__':
    # This block will be executed only if the script is run as the main program
    multiprocessing.freeze_support()  # This is necessary for Windows support
    asyncio.run(main())
