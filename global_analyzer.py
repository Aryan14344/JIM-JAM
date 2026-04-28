import os
import json
import zstandard as zstd
import pandas as pd
import numpy as np
from sentiment_engine import SentimentEngine

class GlobalRedditAnalyzer:
    """
    Synthesizes data across multiple subreddits to find cross-community patterns.
    """
    def __init__(self, dump_dir="data/reddit/subreddits25"):
        self.dump_dir = dump_dir
        self.user_subreddit_map = {} # user -> set(subreddits)
        self.subreddit_sentiment = {} # subreddit -> average_sentiment
        self.sentiment_engine = SentimentEngine()

    def process_all_subreddits(self, limit_per_sub=5000):
        """
        Samples comments from all subreddits to build the global landscape.
        """
        print(f"[*] Starting Global Scan of {self.dump_dir}...")
        
        all_files = [f for f in os.listdir(self.dump_dir) if f.endswith(".zst")]
        stats = {"success": 0, "failed": 0, "total": len(all_files)}
        
        for filename in all_files:
            subreddit = filename.replace("_comments.zst", "")
            filepath = os.path.join(self.dump_dir, filename)
            
            print(f"    - Processing r/{subreddit}...")
            
            users = set()
            sentiments = []
            count = 0
            
            dctx = zstd.ZstdDecompressor()
            try:
                with open(filepath, 'rb') as fh:
                    with dctx.stream_reader(fh) as reader:
                        import io
                        text_stream = io.TextIOWrapper(reader, encoding='utf-8')
                        
                        for line in text_stream:
                            try:
                                comment = json.loads(line)
                                author = comment.get('author', '[deleted]')
                                if author != '[deleted]':
                                    users.add(author)
                                    
                                    # Add to global user map
                                    if author not in self.user_subreddit_map:
                                        self.user_subreddit_map[author] = set()
                                    self.user_subreddit_map[author].add(subreddit)
                                    
                                    # Sentiment (Sampling for speed)
                                    if count % 10 == 0: # Sample 10% for sentiment
                                        text = comment.get('body', '')
                                        score = self.sentiment_engine.get_sentiment(text)
                                        sentiments.append(score)
                                        
                                count += 1
                                if count >= limit_per_sub:
                                    break
                            except Exception as e:
                                # Log error once per sub if it's something weird
                                if count == 0:
                                    print(f"      [!] Error parsing comment: {e}")
                                continue
                stats["success"] += 1
            except Exception as e:
                print(f"    [!] Error reading {filename}: {e}")
                stats["failed"] += 1
                continue
                
            if sentiments:
                self.subreddit_sentiment[subreddit] = sum(sentiments) / len(sentiments)

        print(f"\n[*] Global Scan Complete.")
        print(f"    - Successfully processed: {stats['success']}")
        print(f"    - Failed/Incomplete: {stats['failed']}")
        print(f"    - Data Coverage: {(stats['success']/stats['total'])*100:.1f}%")

    def verify_data_integrity(self):
        """
        Quickly checks all files to see if they are valid zstd archives.
        """
        print(f"[*] Verifying Data Integrity in {self.dump_dir}...")
        all_files = sorted([f for f in os.listdir(self.dump_dir) if f.endswith(".zst")])
        
        report = []
        for filename in all_files:
            filepath = os.path.join(self.dump_dir, filename)
            status = "OK"
            error_msg = ""
            
            try:
                dctx = zstd.ZstdDecompressor()
                with open(filepath, 'rb') as fh:
                    # Just try to read the first 1KB to verify the header/frame
                    with dctx.stream_reader(fh) as reader:
                        reader.read(1024)
            except Exception as e:
                status = "CORRUPT/INCOMPLETE"
                error_msg = str(e)
            
            report.append({
                "subreddit": filename.replace("_comments.zst", ""),
                "status": status,
                "error": error_msg
            })
        
        return pd.DataFrame(report)

    def calculate_jaccard_similarity(self):
        """
        Computes user-overlap similarity between all subreddits.
        """
        print("[*] Calculating Subreddit Similarity Matrix (Jaccard)...")
        
        # Get list of unique subreddits
        subreddits = sorted(list(self.subreddit_sentiment.keys()))
        n = len(subreddits)
        matrix = np.zeros((n, n))
        
        # Pre-calculate user sets for each subreddit
        sub_users = {sub: set() for sub in subreddits}
        for user, subs in self.user_subreddit_map.items():
            for sub in subs:
                if sub in sub_users:
                    sub_users[sub].add(user)
        
        for i in range(n):
            for j in range(i, n):
                sub1 = subreddits[i]
                sub2 = subreddits[j]
                
                set1 = sub_users[sub1]
                set2 = sub_users[sub2]
                
                intersection = len(set1.intersection(set2))
                union = len(set1.union(set2))
                
                similarity = intersection / union if union > 0 else 0
                matrix[i, j] = similarity
                matrix[j, i] = similarity
                
        return pd.DataFrame(matrix, index=subreddits, columns=subreddits)

    def get_global_brokers(self, top_n=10):
        """
        Identifies users with the highest 'Versatility' (active in most subreddits).
        """
        versatility = {user: len(subs) for user, subs in self.user_subreddit_map.items()}
        sorted_users = sorted(versatility.items(), key=lambda x: x[1], reverse=True)
        return sorted_users[:top_n]

    def get_sentiment_landscape(self):
        """
        Returns a sorted list of subreddits by average sentiment.
        """
        return sorted(self.subreddit_sentiment.items(), key=lambda x: x[1], reverse=True)
