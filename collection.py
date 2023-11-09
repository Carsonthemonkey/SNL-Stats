import argparse
import asyncio
import aiohttp
from tqdm.asyncio import tqdm
from snl_archive_scraper import get_all_episode_urls, get_scenes_from_episode_url
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

        scenes = [dict(scene) for episode in episodes for scene in episode]
        
        #! This data is not writing correctly at the moment
        with open("data/scenes.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(scenes))



asyncio.run(main())