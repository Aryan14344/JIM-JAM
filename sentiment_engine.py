from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentEngine:
    """
    Utility to analyze the sentiment of Reddit interactions.
    Used for creating Signed Graphs (Positive/Negative links).
    """
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def get_sentiment(self, text):
        """
        Returns a polarity score between -1 and 1.
        """
        if not text:
            return 0
        scores = self.analyzer.polarity_scores(text)
        return scores['compound']

    def enrich_interactions(self, interaction_df, comments_dict):
        """
        Adds sentiment scores to the interaction dataframe.
        comments_dict: Mapping of user-interaction-id to text.
        """
        # In a real scenario, we'd have the comment text here.
        # For the blueprint, we assume interaction_df has a 'text' column.
        if 'text' in interaction_df.columns:
            interaction_df['sentiment'] = interaction_df['text'].apply(self.get_sentiment)
        return interaction_df

# Explanation:
# 1. Vader is chosen for its focus on social media language (emojis, slang, intensive punctuation).
# 2. Compound Score: A single metric representing the overall sentiment polarity.
# 3. Use Case: This allows us to move from a standard graph to a 'Signed Graph', 
#    where edges represent Friendship (+) or Hostility (-).
