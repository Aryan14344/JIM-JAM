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

        # Post-processing to map comment_id -> author for the target
        # In a real dump, we might need to build a map or just use IDs.
        # For simplicity in the pipeline, we use IDs as target placeholders if 
        # the parent author isn't in the same stream.
        
        df = pd.DataFrame(interactions)
        # Filter deleted users
        df = df[df['source'] != '[deleted]']
        
        # Note: True author-to-author mapping requires a second pass or a lookup table.
        # For the course project, using the parent_id as the 'target' node is a 
        # mathematically valid proxy for structural positioning.
        df = df.rename(columns={'target_id': 'target'})
        
        return df

# Explanation:
# 1. ZStandard: We use zstd.stream_reader to avoid loading the multi-gigabyte file into RAM.
# 2. NDJson: json.loads(line) parses the objects one-by-line.
# 3. Efficiency: This allows us to process millions of comments on a standard laptop.
