from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def score_comment_sentiment(comment: str) -> float:
    analyzer = SentimentIntensityAnalyzer()
    return analyzer.polarity_scores(comment)['compound']


if __name__ == "__main__":
    # Actual comments on an SNL video
    positive_text = "That was awesome...love her throwing things 😂❤😊😅"
    negative_text = "Heidi's character is very weak. It's a Jost written character and it relies on just throwing things. Unimaginative slapstick is just cheap comedy for morons"
    neutral_text = "Seems like lately Weekend Update has been running a little short. What's up with that"
    analyzer = SentimentIntensityAnalyzer()
    print(score_comment_sentiment(positive_text))
    print(analyzer.polarity_scores(positive_text))
    print(analyzer.polarity_scores(negative_text))
    print(analyzer.polarity_scores(neutral_text))