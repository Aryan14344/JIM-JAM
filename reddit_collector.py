import praw
import pandas as pd
from datetime import datetime

class RedditCollector:
    """
    Principal Blueprint for Reddit Data Acquisition.
    Focuses on Comment-based interaction graphs.
    """
    def __init__(self, client_id, client_secret, user_agent):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    def fetch_subreddit_interactions(self, subreddit_name, limit=100):
        """
        Extracts author -> reply relationships from a subreddit.
        Stores them in a format ready for graph ingestion.
        """
        subreddit = self.reddit.subreddit(subreddit_name)
        interactions = []

        print(f"[*] Mining interactions from r/{subreddit_name}...")
        
        for submission in subreddit.hot(limit=limit):
            submission.comments.replace_more(limit=0) # Flatten comments
            for comment in submission.comments.list():
                if comment.parent_id.startswith('t1_'): # It's a reply to another comment
                    try:
                        parent_comment = self.reddit.comment(id=comment.parent_id[3:])
                        interactions.append({
                            'source': comment.author.name,
                            'target': parent_comment.author.name,
                            'timestamp': comment.created_utc,
                            'subreddit': subreddit_name,
                            'type': 'reply'
                        })
                    except Exception as e:
                        continue # Skip deleted users or comments
        
        df = pd.DataFrame(interactions)
        # Aggregate weights
        df_weighted = df.groupby(['source', 'target', 'subreddit']).agg({
            'timestamp': 'max',
            'type': 'count'
        }).reset_index().rename(columns={'type': 'weight'})
        
        return df_weighted

# Explanation:
# 1. We use PRAW's submission.comments.list() to get a flat view of the conversation thread.
# 2. We identify 'replies' by checking parent_id.
# 3. We aggregate interactions between the same pair of users into a 'weight' attribute.
# 4. This 'weight' is the foundation for our Quantile Pruning in the next step.
