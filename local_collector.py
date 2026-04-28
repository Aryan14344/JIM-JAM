import zstandard as zstd
import json
import pandas as pd
import os

class LocalDumpCollector:
    """
    Principal Architect module for high-speed processing of 
    ZStandard compressed Reddit NDJson dumps.
    """
    def __init__(self, dump_dir):
        self.dump_dir = dump_dir

    def stream_subreddit(self, subreddit_name, limit=10000):
        """
        Decompresses and parses the .zst dump for a specific subreddit.
        - subreddit_name: e.g. 'wallstreetbets'
        """
        filename = f"{subreddit_name}_comments.zst"
        filepath = os.path.join(self.dump_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"[!] Error: File {filepath} not found.")
            return pd.DataFrame()

        print(f"[*] Extracting archival cascades from {filename}...")
        
        interactions = []
        count = 0
        
        # Initialize decompressor
        dctx = zstd.ZstdDecompressor()
        
        with open(filepath, 'rb') as fh:
            with dctx.stream_reader(fh) as reader:
                # Use a buffer to read line-by-line
                import io
                text_stream = io.TextIOWrapper(reader, encoding='utf-8')
                
                for line in text_stream:
                    try:
                        comment = json.loads(line)
                        
                        # We only care about replies to other comments (t1_)
                        # Note: In dumps, parent_id might not have the prefix or might be different
                        parent_id = comment.get('parent_id', '')
                        
                        interactions.append({
                            'source': comment.get('author', '[deleted]'),
                            'target_id': parent_id,
                            'comment_id': comment.get('id', ''),
                            'timestamp': comment.get('created_utc', 0),
                            'subreddit': subreddit_name,
                            'text': comment.get('body', '')
                        })
                        
                        count += 1
                        if count >= limit:
                            break
                    except Exception as e:
                        continue

        df = pd.DataFrame(interactions)
        if df.empty:
            return df

        # Filter deleted users
        df = df[df['source'] != '[deleted]']
        
        # 1. Map parent_id to actual author if available in the same batch
        # parent_id looks like 't1_abc123'
        df['target'] = df['target_id'].apply(lambda x: x.split('_')[-1] if '_' in str(x) else x)
        
        # Build ID -> Author map from current batch
        id_to_author = dict(zip(df['comment_id'], df['source']))
        
        # Attempt to replace target IDs with actual author names
        df['target_author'] = df['target'].map(id_to_author)
        
        # If target author is not found in batch, we use the ID as a proxy (common in SNA)
        df['target'] = df['target_author'].fillna(df['target'])
        
        # 2. AGGREGATE: Turn raw interactions into weighted edges
        # This is CRITICAL for the AntiFluffEngine
        print(f"[*] Aggregating {len(df)} interactions into weighted edges...")
        
        # Calculate weights separately to ensure perfect alignment
        weights = df.groupby(['source', 'target']).size().reset_index(name='weight')
        
        # Aggregate other features
        df_weighted = df.groupby(['source', 'target']).agg({
            'timestamp': 'max',
            'text': lambda x: " ".join(map(str, x))
        }).reset_index()
        
        # Merge weight back in
        df_final = pd.merge(df_weighted, weights, on=['source', 'target'])
        
        return df_final

# Explanation:
# 1. ZStandard: We use zstd.stream_reader to avoid loading the multi-gigabyte file into RAM.
# 2. NDJson: json.loads(line) parses the objects one-by-line.
# 3. Efficiency: This allows us to process millions of comments on a standard laptop.
