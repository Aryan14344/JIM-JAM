import sys
import pandas as pd
from reddit_collector import RedditCollector
from local_collector import LocalDumpCollector
from torrent_downloader import TorrentManager
from config import TARGET_SUBREDDITS
import os
from processing_engine import AntiFluffEngine
from sentiment_engine import SentimentEngine
from latent_modeler import LatentModeler
from advanced_analytics import AdvancedAnalytics
from diffusion_simulator import DiffusionSimulator
from visualizer import SocialVisualizer

def run_pipeline(subreddit_name, praw_creds, mode='auto'):
    print(f"=== Starting Reddit SNA Pipeline ===")
    
    # 1. Collection (Automatic Source Selection)
    dump_path = f"data/{subreddit_name}_comments.zst"
    
    if os.path.exists(dump_path) and (mode == 'auto' or mode == 'archive'):
        # ARCHIVE MODE: Fast processing of local dumps
        print(f"[*] Found local archival data for r/{subreddit_name}. Switching to ARCHIVE mode.")
        collector = LocalDumpCollector(dump_dir="data")
        df_raw = collector.stream_subreddit(subreddit_name, limit=20000)
    elif mode == 'live':
        print(f"[*] Connecting to Reddit API (LIVE mode)...")
        collector = RedditCollector(
            client_id=praw_creds['client_id'],
            client_secret=praw_creds['client_secret'],
            user_agent=praw_creds['user_agent']
        )
        df_raw = collector.fetch_subreddit_interactions(subreddit_name, limit=50)
    else:
        # Fallback to help message
        print(f"[!] Error: No local data found for r/{subreddit_name} and LIVE mode was not requested.")
        print(f"[*] Please download the .zst dump and place it in the 'data/' folder.")
        sys.exit(1)

    # 2. Sentiment Enrichment (Anti-Fluff Feature)
    print("[*] Enriching interactions with sentiment...")
    # (Mock text for demonstration if collector doesn't provide it)
    if 'text' not in df_raw.columns:
        df_raw['text'] = "Mock comment text for r/" + subreddit_name
    
    sentiment_engine = SentimentEngine()
    df_enriched = sentiment_engine.enrich_interactions(df_raw, {})
    
    # 3. Processing (Quantile Pruning)
    engine = AntiFluffEngine(df_enriched)
    G = engine.prune_edges(q=0.5) # Focus on top 50% signal
    
    # 4. Latent Modeling
    modeler = LatentModeler(G)
    embeddings = modeler.generate_embeddings(dimensions=16, walk_length=10, num_walks=50)
    projection = modeler.project_to_2d()
    SocialVisualizer.plot_umap(projection)
    print("[*] Latent Mapping Complete. Visualization saved as latent_map.png")
    
    # 5. Advanced Analytics (Brokers & Motifs)
    analytics = AdvancedAnalytics(G)
    brokers = analytics.calculate_structural_holes()
    print(f"[*] Top 5 Brokers identified: {brokers.index[:5].tolist()}")
    SocialVisualizer.plot_degree_distribution(G)
    
    # 6. Diffusion Simulation
    seeds = brokers.index[:2].tolist() if not brokers.empty else []
    if seeds:
        simulator = DiffusionSimulator(G)
        active, history = simulator.run_icm(seeds, p=0.2)
        print(f"[*] Simulation complete. Final Reach: {len(active)} users.")
        SocialVisualizer.plot_diffusion_curve(history)
        print("[*] Diffusion visualization saved as diffusion_curve.png")

    print("=== Pipeline Execution Finished Successfully ===")

if __name__ == "__main__":
    # In a real scenario, these would come from env vars or a config file
    creds = {
        'client_id': 'YOUR_CLIENT_ID',
        'client_secret': 'YOUR_CLIENT_SECRET',
        'user_agent': 'SNA_Bot_v1.0'
    }
    
    # 1. Setup mode (Download Data)
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        MAGNET = "magnet:?xt=urn:btih:3e3f64dee22dc304cdd2546254ca1f8e8ae542b4&tr=https%3A%2F%2Facademictorrents.com%2Fannounce.php&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce"
        manager = TorrentManager()
        manager.download_subreddits(MAGNET, subreddit_list=TARGET_SUBREDDITS)
        sys.exit(0)

    # 2. Pipeline mode
    mode = sys.argv[2] if len(sys.argv) > 2 else "auto"
    target_sub = sys.argv[1] if len(sys.argv) > 1 else "dataisbeautiful"
    run_pipeline(target_sub, creds, mode=mode)
