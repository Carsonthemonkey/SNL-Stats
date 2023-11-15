from fuzzywuzzy import process, fuzz


def get_matching_string(string: str, strings: list, threshold: float = 0.8) -> str:
    result = process.extractOne(string, strings, score_cutoff=threshold*100, scorer=fuzz.token_sort_ratio)
    if result is not None:
        return result[0]



if __name__ == "__main__":
    print(
        get_matching_string(
            "A Message from Mark Zuckerberg - Saturday Night Live",
            [
                "whiteout",
                "Dumb Jeopardy",
                "Angry Birds",
                "Lost in New York",
                "A Message from Mark Zuckerberg"
            ],
        )
    )
