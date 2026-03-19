import networkx as nx
import pandas as pd
from networkx.algorithms import community
import os
from src.data_loader import load_ego_network, load_combined_network

def detect_communities(G):
    """
    Detects communities in the graph using the Louvain method.
    """
    # Louvain is efficient for medium-sized graphs
    communities_list = community.louvain_communities(G, seed=42)
    return list(communities_list)

def calculate_centrality(G):
    """
    Calculates various centrality measures for nodes in the graph.
    """
    degree_cent = nx.degree_centrality(G)
    
    # Betweenness is slow for large graphs, so we limit it or use samples if needed
    if G.number_of_nodes() > 2000:
        # Approximate betweenness for large graphs
        betweenness_cent = nx.betweenness_centrality(G, k=100)
    else:
        betweenness_cent = nx.betweenness_centrality(G)
        
    eigenvector_cent = nx.eigenvector_centrality(G, max_iter=1000)
    
    centrality_df = pd.DataFrame({
        'node_id': list(G.nodes()),
        'degree_centrality': [degree_cent[node] for node in G.nodes()],
        'betweenness_centrality': [betweenness_cent[node] for node in G.nodes()],
        'eigenvector_centrality': [eigenvector_cent[node] for node in G.nodes()]
    })
    
    return centrality_df.sort_values(by='degree_centrality', ascending=False)

if __name__ == "__main__":
    # Test analysis
    try:
        G, _, _ = load_ego_network("0")
        print("Analyzing Ego 0...")
        comms = detect_communities(G)
        print(f"Communities: {len(comms)}")
        cent = calculate_centrality(G)
        print(cent.head())
    except Exception as e:
        print(f"Error analyzing: {e}")
