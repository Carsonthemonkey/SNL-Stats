import argparse
from typing import List
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import asyncio
import datetime
import json
import logging
import numpy as np
import aiohttp
from tqdm.asyncio import tqdm
from tqdm import tqdm as sync_tqdm
from schema import Sketch
from data_collection.snl_archive_scraper import (
    get_all_episode_urls,
    get_scenes_from_episode_url,
)
from data_collection.youtube import (
    fetch_all_channel_videos,
    fetch_video_statistics,
    fetch_video_comments,
)
from data_collection.fuzzy_search import get_matching_string
from analysis.load_data import load_scene_data, load_video_data, load_full_data
from analysis.sentiment import score_comment_sentiment


async def main():
    logging.info("Starting data collection")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scrape-scenes",
        help="fetch up to date scene data instead of relying on stored data",
        action="store_true",
    )
    parser.add_argument(
        "--refilter",
        help="re-filter stored videos based on title. This is done automatically if scenes or videos are re-scraped",
        action="store_true",
    )
    parser.add_argument(
        "--get-videos",
        help="get ids and titles of all channel's videos from the youtube api",
        action="store_true",
    )
    parser.add_argument(
        "--get-stats",
        help="get all video statistics from the youtube api",
        action="store_true",
    )
    parser.add_argument(
        "--analyze-comments",
        help="fetch and analyze video comment sentiment",
        action="store_true",
    )
    parser.add_argument("--all", "-a", help="re-collect all data", action="store_true")

    args = parser.parse_args()

    # Load or collect scene data
    if args.scrape_scenes or args.all:
        logging.info("Scraping scene data")
        async with aiohttp.ClientSession() as session:
            urls = await get_all_episode_urls(session)
            print(f"found {len(urls)} episodes")
            pbar = tqdm(total=len(urls), desc="Collecting scene data")

            def on_complete(_):
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
        logging.info("Saved scene data to file")
    else:
        scenes = load_scene_data()
        logging.info("Loaded scene data from file")

    # Collect or load titles and ids of all SNL videos
    if args.get_videos or args.all:
        logging.info("Fetching channel videos from youtube")
        # collect titles and ids of all SNL videos
        channel_videos = _fetch_identification_for_all_videos("SaturdayNightLive")
        with open("data/channel_videos.json", "w", encoding="utf-8") as f:
            data = {
                "last_collected": datetime.datetime.now().isoformat(),
                "channel_videos": channel_videos,
            }
            json.dump(data, f, indent=4)
    else:
        # load titles and ids of all SNL videos
        channel_videos = load_video_data()
        logging.info("Loaded channel videos from file")

    if args.refilter or args.all or args.scrape_scenes or args.get_videos:
        # match videos based on title (get video id, title, scene type, and cast)
        filtered_videos = _filter_videos(channel_videos)
        sketch_data = _combine_archive_with_filtered_videos(scenes, filtered_videos)
        full_data = [Sketch(**sketch) for sketch in sketch_data]
    else:
        # load data from previous collection
        full_data = load_full_data()

    # collect youtube data
    if args.get_stats or args.all:
        video_stats = _fetch_youtube_stats(full_data)

        for video in video_stats:
            for sketch in full_data:
                if video['video_id'] == sketch.id:
                    sketch.view_count = video['view_count']
                    sketch.like_count = video['like_count']
                    sketch.comment_count = video['comment_count']
                    sketch.duration = video['duration']
                    sketch.upload_date = video['upload_date']
                    break

    # Collect or load comment sentiment
    if args.analyze_comments or args.all:
        await update_video_sentiment_stats(full_data)

    # Save final composite data
    with open("data/full_data.json", "w", encoding="utf-8") as f:
        data = {
            "last_collected": datetime.datetime.now().isoformat(),
            "full_data": [sketch.model_dump() for sketch in full_data],
        }
        json.dump(data, f, indent=4)
    logging.info("Saved collected data to full_data.json")


async def update_video_sentiment_stats(sketches: List[Sketch]):
    """Adds the comment sentiment fields to the video data. It modifies the passed list, so there are no return values"""
    # filter out sketches that already have their sentiment stats calculated
    sketches = [
        sketch
        for sketch in sketches
        if sketch.mean_sentiment is None or sketch.std_sentiment is None
    ]
    async with aiohttp.ClientSession(timeout=15) as session:
        semaphore = asyncio.Semaphore(15)
        with ProcessPoolExecutor(multiprocessing.cpu_count()) as executor:
            tasks = [
                asyncio.create_task(
                    fetch_and_analyze_comments(video, session, semaphore, executor)
                )
                for video in sketches
            ]

            pbar = tqdm(
                total=len(tasks),
                desc="Analyzing video comments",
                unit=" videos analyzed",
            )

            def on_complete(_):
                pbar.update(1)

            for task in tasks:
                task.add_done_callback(on_complete)

            await asyncio.gather(*tasks)
    


async def fetch_and_analyze_comments(
    sketch: Sketch,
    session: aiohttp.ClientSession(),
    semaphore: asyncio.Semaphore,
    executor: ProcessPoolExecutor,
):
    sentiment_analysis_tasks = []
    async for comment_chunk in fetch_video_comments(sketch.id, session, semaphore):
        tasks = [
            asyncio.create_task(multi_core_sentiment_analysis(comment, executor))
            for comment in comment_chunk
        ]
        sentiment_analysis_tasks.extend(tasks)

    sentiment_results = np.array(await asyncio.gather(*sentiment_analysis_tasks))
    sketch.mean_sentiment = sentiment_results.mean()
    sketch.std_sentiment = sentiment_results.std()
    logging.info(
        "Analyzed comments for %s. Mean: %s, Std: %s from %s comments",
        sketch.title,
        sketch.mean_sentiment,
        sketch.std_sentiment,
        len(sentiment_results),
    )


async def multi_core_sentiment_analysis(comment: str, executor: ProcessPoolExecutor):
    future = executor.submit(score_comment_sentiment, comment)
    return await asyncio.wrap_future(future)


def _fetch_identification_for_all_videos(username: str) -> list:
    # collect titles and ids of all SNL videos
    print("Getting videos from youtube...")
    channel_videos = fetch_all_channel_videos(username)
    return channel_videos


def _filter_videos(channel_videos: list) -> list:
    blocked_strings = ["behind the sketch", "behind the scenes", "bloopers", "(live)"] # Use this to manually filter titles
    required_strings = ["- SNL", "- Saturday Night Live"]
    filtered_videos = [
        video
        for video in channel_videos
        if (video["title"] is not None 
            and any(r in video["title"] for r in required_strings) 
            and not any(blocked in video["title"].lower() for blocked in blocked_strings))
        
    ]

    # Remove "SNL" and "Saturday Night Live" from titles
    for video in filtered_videos:
        for r in required_strings:
            video["title"] = video["title"].replace(r, "").strip()

    return filtered_videos


def _combine_archive_with_filtered_videos(scenes: dict, filtered_videos: list) -> dict:
    composite_data = []
    scene_titles = [
        scene["title"] for scene in scenes["scene_data"] if scene["title"] is not None
    ]
    # load function args into list of tuples for multiprocessing
    args = [
        (vid, scene_titles, scenes["scene_data"])
        for vid in filtered_videos
        if vid["title"] is not None
    ]
    num_processes = multiprocessing.cpu_count()
    print(f"Utilizing {num_processes} CPU cores for title matching")
    with multiprocessing.Pool(processes=num_processes) as pool:
        for result in sync_tqdm(
            pool.imap_unordered(_multi_core_wrapper, args),
            total=len(args),
            desc="Indexing video titles",
        ):
            if result is not None:
                composite_data.append(result)

    return composite_data


def _multi_core_wrapper(args: tuple):
    return _get_combined_data_from_video_info(*args)


def _get_combined_data_from_video_info(
    video_info: dict, scene_titles, scene_data: list
) -> dict:
    matching_scene_title = get_matching_string(video_info["title"], scene_titles, 0.9)
    if matching_scene_title is not None:
        logging.info('matched video: "%s" with scene "%s"', video_info['title'], matching_scene_title)
        # print(f'matched video: "{video_info['title']}" with scene "{matching_scene_title}"')
        matching_scene = _get_scene_by_title(matching_scene_title, scene_data)
        matched_video = {"id": video_info["id"], **matching_scene}
        return matched_video


def _get_scene_by_title(title: str, scenes: list) -> dict:
    for scene in scenes:
        if scene["title"] == title:
            return scene


def _fetch_youtube_stats(sketch_data: List[Sketch]) -> list:
    id_list = _get_ids(sketch_data)
    video_stats = fetch_video_statistics(id_list)
    return video_stats  # TODO: might want to return updated sketch_data instead?


def _get_ids(sketch_data: List[Sketch]) -> list:
    ids = [sketch.id for sketch in sketch_data]
    return ids


def _fetch_youtube_stats(sketch_data: List[Sketch]) -> list:
    id_list = _get_ids(sketch_data)
    video_stats = fetch_video_statistics(id_list)
    return video_stats  # TODO: might want to return updated sketch_data instead?


def _get_ids(sketch_data: List[Sketch]) -> list:
    ids = [sketch.id for sketch in sketch_data]
    return ids

def clear_sentiment():
    full_data = load_full_data()
    for sketch in full_data:
        sketch.mean_sentiment = None
        sketch.std_sentiment = None
    with open("data/full_data.json", "w", encoding="utf-8") as f:
        data = {
            "last_collected": datetime.datetime.now().isoformat(),
            "full_data": [sketch.model_dump() for sketch in full_data],
        }
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, filemode="w", filename="logs/collection.log"
    )
    multiprocessing.freeze_support()
    asyncio.run(main())
