import sys
import pandas as pd
from reddit_collector import RedditCollector
from processing_engine import AntiFluffEngine
from sentiment_engine import SentimentEngine
from latent_modeler import LatentModeler
from advanced_analytics import AdvancedAnalytics
from diffusion_simulator import DiffusionSimulator
from visualizer import SocialVisualizer

def run_pipeline(subreddit_name, praw_creds):
    print(f"=== Starting Reddit SNA Pipeline for r/{subreddit_name} ===")
    
    # 1. Collection
    collector = RedditCollector(
        client_id=praw_creds['client_id'],
        client_secret=praw_creds['client_secret'],
        user_agent=praw_creds['user_agent']
    )
    # Using a small limit for demonstration
    df_raw = collector.fetch_subreddit_interactions(subreddit_name, limit=10)
    
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
    
    target_sub = sys.argv[1] if len(sys.argv) > 1 else "dataisbeautiful"
    run_pipeline(target_sub, creds)
