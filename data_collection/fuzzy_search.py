from fuzzywuzzy import process


def get_matching_string(title: str, titles: list) -> str:
    return process.extractOne(title, titles)


if __name__ == '__main__':
    print(get_matching_string("Angry birds - SNL", ["whiteout", "Dumb Jeopardy", "Angry Birds", "Lost in New York"]))
