import argparse
import asyncio
import aiohttp
from tqdm.asyncio import tqdm
from data_collection.snl_archive_scraper import get_all_episode_urls, get_scenes_from_episode_url
from analysis.load_data import load_scene_data
import datetime
import json

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scrape-scenes",
        help="fetch up to date scene data instead of relying on stored data",
        action="store_true",
    )
    parser.add_argument('--all', '-a', help="re-collect all data", action='store_true')

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
            tasks = [asyncio.create_task(get_scenes_from_episode_url(url, session, semaphore)) for url in urls]

            for task in tasks:
                task.add_done_callback(on_complete)

            episodes = await asyncio.gather(*tasks)
        scenes = [dict(scene) for episode in episodes if episode is not None for scene in episode if scene is not None]

        with open("data/scenes.json", "w", encoding="utf-8") as f:
            data = {
                "last_collected": datetime.datetime.now().isoformat(),
                "scene_data": scenes
            }
            json.dump(data, f, indent=4)
    else:
        scenes = load_scene_data()
    

    # Collect or load youtube stats

    # Collect or load comment sentiment

asyncio.run(main())