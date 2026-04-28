import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd

from local_collector import LocalDumpCollector
from processing_engine import AntiFluffEngine
from sentiment_engine import SentimentEngine
from advanced_analytics import AdvancedAnalytics
from latent_modeler import LatentModeler
from diffusion_simulator import DiffusionSimulator
from visualizer import SocialVisualizer

DUMP_DIR = "data/reddit/subreddits25"
PROCESSED_DIR = "data/processed"
GRAPHS_DIR = "data/graphs"
PLOTS_DIR = "data/plots"

def run_pipeline_for_subreddit(filename, limit=20000):
    """
    Worker function to process a single subreddit through the SNA pipeline.
    It builds the interaction graph, calculates shadow brokers, and saves both artifacts.
    """
    if not filename.endswith("_comments.zst"):
        return None
        
    subreddit_name = filename.replace("_comments.zst", "")
    brokers_output = os.path.join(PROCESSED_DIR, f"{subreddit_name}_shadow_brokers.csv")
    graph_output = os.path.join(GRAPHS_DIR, f"{subreddit_name}_graph.csv")
    
    umap_output = os.path.join(PLOTS_DIR, f"{subreddit_name}_latent_map.png")
    degree_output = os.path.join(PLOTS_DIR, f"{subreddit_name}_degree_distribution.png")
    diffusion_output = os.path.join(PLOTS_DIR, f"{subreddit_name}_diffusion_curve.png")
    
    # Skip only if ALL artifacts exist
    if (os.path.exists(brokers_output) and 
        os.path.exists(graph_output) and 
        os.path.exists(umap_output)):
        return f"{subreddit_name:20} -> Skipped (Already exists)"
        
    try:
        # 1. Collect Data (Limiting for batch speed)
        collector = LocalDumpCollector(dump_dir=DUMP_DIR)
        df_raw = collector.stream_subreddit(subreddit_name, limit=limit)
        
        if df_raw.empty:
            raise ValueError("Empty Data")
            
        # 2. Enrich & Prune to Build Graph
        if 'text' not in df_raw.columns:
            df_raw['text'] = ""
        sentiment_engine = SentimentEngine()
        df_enriched = sentiment_engine.enrich_interactions(df_raw, {})
        
        engine = AntiFluffEngine(df_enriched)
        G = engine.prune_edges(q=0.5)
        
        if len(G.nodes) == 0:
            raise ValueError("Graph empty after pruning")
            
        # --- EXPORT GRAPH ---
        engine.export_processed_data(graph_output)
        
        modeler = LatentModeler(G)
        embeddings = modeler.generate_embeddings(dimensions=64, walk_length=30, num_walks=100)
        projection = modeler.project_to_2d()
        SocialVisualizer.plot_umap(projection, filename=umap_output)

        # 3. Analytics (Find Shadow Brokers via Structural Holes)
        analytics = AdvancedAnalytics(G)
        brokers = analytics.calculate_structural_holes()
        
        # --- EXPORT BROKERS ---
        brokers.to_csv(brokers_output, index_label="User")
        
        # --- GENERATE PLOTS ---
        # Degree Distribution
        SocialVisualizer.plot_degree_distribution(G, filename=degree_output)
        
        # Latent Modeling (UMAP)
        # Using fewer dimensions and walks for speed during batch processing
        
        # Diffusion Simulator
        seeds = brokers.index[:5].tolist() if not brokers.empty else []
        if seeds:
            simulator = DiffusionSimulator(G)
            active, history = simulator.run_icm(seeds, p=0.2)
            SocialVisualizer.plot_diffusion_curve(history, filename=diffusion_output)
        
        return f"{subreddit_name:20} -> Success (Nodes: {len(G.nodes)}, Edges: {len(G.edges)})"
        
    except Exception as e:
        return f"{subreddit_name:20} -> Error ({str(e)})"


def run_batch():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(GRAPHS_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)
    files = [f for f in os.listdir(DUMP_DIR) if f.endswith(".zst")]
    
    print(f"=== Starting Batch Pipeline Execution ({len(files)} subreddits) ===")
    
    workers = min(os.cpu_count() or 4, 16)
    print(f"[*] Running with {workers} parallel processes...\n")
    print(f"[*] Output Directories:")
    print(f"    - Graphs:  {GRAPHS_DIR}/")
    print(f"    - Brokers: {PROCESSED_DIR}/")
    print(f"    - Plots:   {PLOTS_DIR}/\n")
    
    success_count = 0
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(run_pipeline_for_subreddit, f): f for f in files}
        
        for i, future in enumerate(as_completed(futures), 1):
            res = future.result()
            if res:
                print(f"[{i:02d}/{len(files):02d}] {res}")
                if "Success" in res:
                    success_count += 1
                
    print(f"\n=== Batch Pipeline Complete. Processed {success_count} subreddits successfully. ===")

if __name__ == "__main__":
    run_batch()
