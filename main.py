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
from global_analyzer import GlobalRedditAnalyzer

def run_pipeline(subreddit_name, praw_creds, mode='auto'):
    print(f"=== Starting Reddit SNA Pipeline ===")
    
    # 1. Collection (Automatic Source Selection)
    # We check for the file in the data/ directory
    dump_dir = "data/reddit/subreddits25"
    dump_path = os.path.join(dump_dir, f"{subreddit_name}_comments.zst")
    
    if os.path.exists(dump_path) and (mode == 'auto' or mode == 'archive'):
        # ARCHIVE MODE: Fast processing of local dumps
        print(f"[*] Found local archival data for r/{subreddit_name}. Switching to ARCHIVE mode.")
        collector = LocalDumpCollector(dump_dir=dump_dir)
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
        print(f"[*] Expected file: {dump_path}")
        sys.exit(1)

    # Safety check: Ensure we actually got data back
    if df_raw.empty:
        print(f"[!] Error: Interaction data is empty for r/{subreddit_name}.")
        print(f"[*] Check if {dump_path} exists and is not empty.")
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
    
    # Export cleaned data
    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)
    export_path = os.path.join(processed_dir, f"{subreddit_name}_cleaned.csv")
    engine.export_processed_data(export_path)
    
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

def run_global_analysis():
    print("=== Starting Global Cross-Subreddit Analysis ===")
    analyzer = GlobalRedditAnalyzer()
    
    # Process data (sampling 5000 comments per sub for speed)
    analyzer.process_all_subreddits(limit_per_sub=5000)
    
    # 1. Similarity Matrix
    similarity_df = analyzer.calculate_jaccard_similarity()
    SocialVisualizer.plot_similarity_heatmap(similarity_df)
    print("[*] Global Similarity Matrix saved as global_similarity_matrix.png")
    
    # 2. Sentiment Landscape
    landscape = analyzer.get_sentiment_landscape()
    SocialVisualizer.plot_global_sentiment(landscape)
    print("[*] Global Sentiment Landscape saved as global_sentiment_landscape.png")
    
    # 3. Global Brokers
    brokers = analyzer.get_global_brokers(top_n=10)
    print("\n[*] TOP 10 GLOBAL BROKERS (Community Bridgers):")
    for user, count in brokers:
        print(f"    - {user}: active in {count} subreddits")
    
    print("\n=== Global Analysis Finished Successfully ===")

def run_verification():
    print("=== Starting Data Integrity Check ===")
    analyzer = GlobalRedditAnalyzer()
    report_df = analyzer.verify_data_integrity()
    
    corrupt = report_df[report_df['status'] != 'OK']
    
    if corrupt.empty:
        print("[+] All files verified successfully. Ready for full analysis.")
    else:
        print(f"[!] Found {len(corrupt)} incomplete or corrupt files:")
        for _, row in corrupt.iterrows():
            print(f"    - r/{row['subreddit']}: {row['error']}")
        print("\n[*] Please ensure qBittorrent has finished downloading these files.")
    
    print("=== Verification Finished ===")

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
    
    # 2. Global Mode
    if len(sys.argv) > 1 and sys.argv[1] == "global":
        run_global_analysis()
        sys.exit(0)
    
    # 3. Verify Mode
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        run_verification()
        sys.exit(0)
    
    # 4. Pipeline mode
    mode = sys.argv[2] if len(sys.argv) > 2 else "auto"
    target_sub = sys.argv[1] if len(sys.argv) > 1 else "dataisbeautiful"
    run_pipeline(target_sub, creds, mode=mode)
