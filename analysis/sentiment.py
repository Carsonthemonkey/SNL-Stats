from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


if __name__ == "__main__":
    # Actual comments on an SNL video
    positive_text = "That was awesome...love her throwing things 😂❤😊😅"
    negative_text = "Crystal isn't funny."
    neutral_text = "Seems like lately Weekend Update has been running a little short. What's up with that"
    analyzer = SentimentIntensityAnalyzer()
    print(analyzer.polarity_scores(positive_text))
    print(analyzer.polarity_scores(negative_text))
    print(analyzer.polarity_scores(neutral_text))