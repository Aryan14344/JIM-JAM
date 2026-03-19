import os
import sys

# Ensure the project root is in the path so we can run from anywhere
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.data_loader import load_ego_network, load_combined_network
from src.visualize import visualize_network, plot_degree_distribution
from src.analysis import detect_communities, calculate_centrality

def run_analysis(G, name):
    print(f"\n--- Analysis for {name} ---")
    print(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    
    print("Generating visualizations...")
    visualize_network(G, name)
    plot_degree_distribution(G, name)
    
    print("Detecting communities...")
    communities = detect_communities(G)
    print(f"Number of communities detected: {len(communities)}")
    
    print("Calculating centrality measures...")
    centrality_df = calculate_centrality(G)
    
    print("\nTop 5 Influential Nodes:")
    print(centrality_df[['node_id', 'degree_centrality', 'betweenness_centrality']].head(5))

def main():
    # 1. Analyze an Ego Network
    try:
        ego_id = "0"
        G_ego, _, _ = load_ego_network(ego_id)
        run_analysis(G_ego, f"ego_{ego_id}")
    except Exception as e:
        print(f"Error analyzing ego network: {e}")
        
    # 2. Analyze the Combined Network
    try:
        G_combined = load_combined_network()
        run_analysis(G_combined, "combined_facebook")
    except Exception as e:
        print(f"Error analyzing combined network: {e}")

    print("\nAnalysis complete. Results saved in 'plots/' directory.")

if __name__ == "__main__":
    main()
