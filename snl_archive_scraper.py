import asyncio
import requests
from bs4 import BeautifulSoup
import re

async def get_actors_from_episode_url(url: str) -> list:
    res = requests.get(url, timeout=20)
    # content is initially bytes, so must be cast as a string
    html = res.content
    soup = BeautifulSoup(html, 'html.parser')
    class_regex = re.compile('card-sketch.*')
    cards = soup.find(id='full').find_all(class_=class_regex)
    for card in cards:
        print(get_card_type(card))
    # inside div id full
    return [card.prettify() for card in cards]
    # card is div with classes 'card' and 'card-sketch...' has class card

def get_card_type(card) -> str:
    return card.find(name='table', class_='sketch-title').tbody.tr.td.a.span.contents[0]

if __name__ == "__main__":
    result = asyncio.run(get_actors_from_episode_url("http://www.snlarchives.net/Episodes/?20200307"))
    # print(result)
    with open('index.html', 'w') as f:
        for card in result:
            f.write(card)