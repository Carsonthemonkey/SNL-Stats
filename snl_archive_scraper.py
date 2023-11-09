import asyncio
import re
import requests
import bs4
from bs4 import BeautifulSoup
from schema import Scene
from typing import List
import json

async def get_all_episode_urls():
    BASE_URL = "http://www.snlarchives.net/Episodes/"
    res = requests.get(BASE_URL, timeout=20)
    soup = BeautifulSoup(res.content, 'html.parser')
    chunks = soup.find_all(name='table', class_='sketch-roles')
    urls = []
    for chunk in chunks:
        for tag in chunk.children:
            if isinstance(tag, bs4.NavigableString) or tag is None:
                continue
            urls.append(BASE_URL + tag.td.a['href'])
    return urls

async def get_scenes_from_episode_url(url: str) -> List[Scene]:
    res = requests.get(url, timeout=20)
    soup = BeautifulSoup(res.content, 'html.parser')

    # card is div with classes 'card' and 'card-sketch...' has class card
    class_regex = re.compile('card-sketch.*')
    # inside div id full
    cards = soup.find(id='full').find_all(class_=class_regex)
    return [Scene(
        title=get_scene_title(card),
        scene_type=get_scene_type(card),
        cast=get_scene_actors(card)
    ) for card in cards]
    
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

if __name__ == "__main__":
    episodes = asyncio.run(get_all_episode_urls())
    for episode in episodes:
        print(episode)
    # result = asyncio.run(get_scenes_from_episode_url("http://www.snlarchives.net/Episodes/?20200307"))
    # print(result)
    # with open('scenes.json', 'w') as f:
    #     json.dump([dict(card) for card in result], f)