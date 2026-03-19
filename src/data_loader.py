import os
import networkx as nx
import pandas as pd

# Define data directory relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

def get_data_dir():
    """Returns the absolute path to the data directory."""
    return DATA_DIR

def load_ego_network(ego_id):
    """
    Loads an ego network from the SNAP Facebook dataset.
    Returns a networkx graph, features, and circles.
    """
    ego_dir = os.path.join(DATA_DIR, "facebook")
    
    # Load edges
    edges_file = os.path.join(ego_dir, f"{ego_id}.edges")
    if not os.path.exists(edges_file):
        raise FileNotFoundError(f"Edges file not found: {edges_file}")
    
    G = nx.read_edgelist(edges_file, nodetype=int)
    
    # Add the ego node itself and connect it to all its friends
    ego_id_int = int(ego_id)
    G.add_node(ego_id_int)
    for node in list(G.nodes()):
        if node != ego_id_int:
            G.add_edge(ego_id_int, node)
            
    # Load feature names
    featnames_file = os.path.join(ego_dir, f"{ego_id}.featnames")
    if os.path.exists(featnames_file):
        with open(featnames_file, 'r') as f:
            feat_names = [line.strip().split(' ', 1)[1] for line in f]
    else:
        feat_names = []

    # Load node features
    feat_file = os.path.join(ego_dir, f"{ego_id}.feat")
    if os.path.exists(feat_file):
        feats = pd.read_csv(feat_file, sep=' ', header=None, index_col=0)
        if feat_names:
            feats.columns = feat_names
    else:
        feats = pd.DataFrame()
    
    # Load ego feature
    egofeat_file = os.path.join(ego_dir, f"{ego_id}.egofeat")
    if os.path.exists(egofeat_file):
        with open(egofeat_file, 'r') as f:
            ego_feat = [int(x) for x in f.read().strip().split(' ')]
        feats.loc[ego_id_int] = ego_feat
    
    # Load circles (communities)
    circles_file = os.path.join(ego_dir, f"{ego_id}.circles")
    circles = {}
    if os.path.exists(circles_file):
        with open(circles_file, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                circle_id = parts[0]
                members = [int(x) for x in parts[1:]]
                circles[circle_id] = members
                
    return G, feats, circles

def load_combined_network():
    """
    Loads the combined ego networks (facebook_combined.txt).
    """
    combined_file = os.path.join(DATA_DIR, "facebook_combined.txt")
    if not os.path.exists(combined_file):
         # Try in subfolder just in case
         combined_file = os.path.join(DATA_DIR, "facebook", "facebook_combined.txt")
         
    if not os.path.exists(combined_file):
        raise FileNotFoundError(f"Combined edges file not found: {combined_file}")
        
    G = nx.read_edgelist(combined_file, nodetype=int)
    return G

if __name__ == "__main__":
    # Test loading
    try:
        G, feats, circles = load_ego_network("0")
        print(f"Ego 0 Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
        G_combined = load_combined_network()
        print(f"Combined Network: {G_combined.number_of_nodes()} nodes, {G_combined.number_of_edges()} edges")
    except Exception as e:
        print(f"Error loading: {e}")
