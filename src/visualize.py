import matplotlib.pyplot as plt
import networkx as nx
import os
from src.data_loader import load_ego_network, load_combined_network, get_data_dir

def visualize_network(G, name, output_dir="plots"):
    """
    Visualizes the graph and saves it to a file.
    """
    project_root = os.path.dirname(get_data_dir())
    output_path = os.path.join(project_root, output_dir)
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        
    plt.figure(figsize=(10, 8))
    # Use a faster layout for larger graphs if needed
    if G.number_of_nodes() > 1000:
        pos = nx.random_layout(G)
    else:
        pos = nx.spring_layout(G, seed=42)
        
    nx.draw(G, pos, node_size=10, with_labels=False, alpha=0.3, node_color='blue', edge_color='gray')
    plt.title(f"Social Network: {name}")
    plt.savefig(os.path.join(output_path, f"{name}_network.png"))
    plt.close()

def plot_degree_distribution(G, name, output_dir="plots"):
    """
    Plots the degree distribution of the graph.
    """
    project_root = os.path.dirname(get_data_dir())
    output_path = os.path.join(project_root, output_dir)
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        
    degrees = [d for n, d in G.degree()]
    plt.figure(figsize=(8, 6))
    plt.hist(degrees, bins=50, color='skyblue', edgecolor='black')
    plt.title(f"Degree Distribution: {name}")
    plt.xlabel("Degree")
    plt.ylabel("Frequency")
    plt.savefig(os.path.join(output_path, f"{name}_degree_dist.png"))
    plt.close()

if __name__ == "__main__":
    # Test visualization
    try:
        G, _, _ = load_ego_network("0")
        visualize_network(G, "ego_0")
        plot_degree_distribution(G, "ego_0")
        print("Ego 0 plots generated.")
    except Exception as e:
        print(f"Error visualizing: {e}")
