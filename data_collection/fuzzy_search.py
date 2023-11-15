from fuzzywuzzy import process


def get_matching_string(string: str, strings: list) -> str:
    return process.extractOne(string, strings)


if __name__ == '__main__':
    print(get_matching_string("Angry birds - SNL", ["whiteout", "Dumb Jeopardy", "Angry Birds", "Lost in New York"]))
