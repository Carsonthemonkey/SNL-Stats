import asyncio
import re
import requests
import aiohttp
import bs4
from bs4 import BeautifulSoup
from schema import Scene
from typing import List

async def get_all_episode_urls(session: aiohttp.ClientSession):

    BASE_URL = "http://www.snlarchives.net/Episodes/"
    async with session.get(BASE_URL) as res:
        soup = BeautifulSoup(await res.text(), 'html.parser')
    chunks = soup.find_all(name='table', class_='sketch-roles')
    urls = []
    for chunk in chunks:
        for tag in chunk.children:
            if isinstance(tag, bs4.NavigableString) or tag is None:
                continue
            urls.append(BASE_URL + tag.td.a['href'])
    return urls

async def get_scenes_from_episode_url(url: str, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore) -> List[Scene]:
    try:
        async with semaphore:
            async with session.get(url) as res:
                soup = BeautifulSoup(await res.text(), 'html.parser')

            # card is div with classes 'card' and 'card-sketch...' has class card
            class_regex = re.compile('card-sketch.*')
            # inside div id full
            cards = soup.find(id='full').find_all(class_=class_regex)
            # print("done")
            return [Scene(
                title=get_scene_title(card),
                scene_type=get_scene_type(card),
                cast=get_scene_actors(card)
            ) for card in cards]
    except TimeoutError:
        print(f"TimeoutError for url: {url}")


    
def get_scene_type(card) -> str:
    return card.find(name='table', class_='sketch-title').tbody.tr.td.a.span.contents[0]

def get_scene_title(card) -> str:
    tag = card.find(name='table', class_='sketch-title').tbody.tr.contents[1].contents
    
    # Monologues have no titles, so this must be handled like so
    if not tag:
        return None
    # Some titles are hyperlinks in which case the inner text of the <a> tag must be extracted
    return str(tag[0]) if isinstance(tag[0], bs4.NavigableString) else str(tag[0].contents[0])

def get_scene_actors(card) -> list:
    actor_regex = re.compile(r'person-\d+')
    actor_tds = card.find_all(name='td', class_=actor_regex)
    actors = []
    for td in actor_tds:
        actor = td.contents[0]
        # handles the actor's name being possibly a link
        actors.append(actor if isinstance(actor, bs4.NavigableString) else actor.contents[0])
    return actors

async def _demo():
    async with aiohttp.ClientSession() as session:
    #     episodes = await get_all_episode_urls(session)
        result = await get_scenes_from_episode_url("http://www.snlarchives.net/Episodes/?20200307", session, asyncio.Semaphore(15))
        print(result)
    # for episode in episodes:
    #     print(episode)

if __name__ == "__main__":
    asyncio.run(_demo())
    # print(result)
    # with open('scenes.json', 'w') as f:
    #     json.dump([dict(card) for card in result], f)