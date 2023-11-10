import argparse
import asyncio
import aiohttp
from tqdm.asyncio import tqdm
from snl_archive_scraper import get_all_episode_urls, get_scenes_from_episode_url
import datetime
import json

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scrape-scenes",
        help="fetch up to date scene data instead of relying on stored data",
        action="store_true",
    )

    args = parser.parse_args()

    if args.scrape_scenes:
        print("Scraping scenes...")
        async with aiohttp.ClientSession() as session:
            urls = await get_all_episode_urls(session)
            print(f"found {len(urls)} episodes")
            pbar = tqdm(total=len(urls), desc="Collecting scene data")

            def on_complete(future):
                pbar.update(1)
            tasks = [asyncio.create_task(get_scenes_from_episode_url(url, session)) for url in urls]

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

        # Collect youtube data here

asyncio.run(main())