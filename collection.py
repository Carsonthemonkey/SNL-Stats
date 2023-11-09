import argparse
import asyncio
from snl_archive_scraper import get_all_episode_urls, get_scenes_from_episode_url

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scrape-scenes",
        help="fetch up to date scene data instead of relying on stored data",
        action="store_true",
    )

    args = parser.parse_args()

    if args.scrape_scenes:
        urls = await get_all_episode_urls()
        #TODO: Store orginal air date in the data
        tasks = [asyncio.create_task(get_scenes_from_episode_url(url)) for url in urls]
        episodes = await asyncio.gather(*tasks)
        scenes = [dict(scene) for episode in episodes for scene in episode]
        with open("data/scenes.json") as f:
            f.write(scenes)

asyncio.run(main())