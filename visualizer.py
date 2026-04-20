import matplotlib.pyplot as plt
import networkx as nx

class SocialVisualizer:
    """
    Handles generation of plots for the SNA pipeline.
    """
    @staticmethod
    def plot_umap(projection_df, labels=None):
        """
        Plots the 2D latent map.
        """
        plt.figure(figsize=(10, 8))
        plt.scatter(
            projection_df['UMAP_1'], 
            projection_df['UMAP_2'], 
            c='blue', alpha=0.6, s=50
        )
        plt.title("Latent Interaction Map (UMAP)")
        plt.xlabel("Latent Dim 1")
        plt.ylabel("Latent Dim 2")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.savefig("latent_map.png")
        plt.close()

    @staticmethod
    def plot_diffusion_curve(history):
        """
        Plots the cumulative reach of information over time.
        """
        plt.figure(figsize=(10, 6))
        plt.plot(history, marker='o', linestyle='-', color='red')
        plt.title("Information Diffusion Cascade (Cumulative Reach)")
        plt.xlabel("Iteration (Hop Count)")
        plt.ylabel("Active Nodes")
        plt.grid(True)
        plt.savefig("diffusion_curve.png")
        plt.close()

    @staticmethod
    def plot_degree_distribution(G):
        """
        Visualizes the power-law signature of the network.
        """
        degrees = [d for n, d in G.degree()]
        plt.figure(figsize=(10, 6))
        plt.hist(degrees, bins=20, color='green', alpha=0.7)
        plt.title("Degree Distribution (Scale-Free Check)")
        plt.xlabel("Degree")
        plt.ylabel("Frequency")
        plt.savefig("degree_distribution.png")
        plt.close()

# Explanation:
# 1. Non-Interactive Export: The visualizer saves to .png files, making it 
#    server-friendly for headless environments.
# 2. Power-Law Check: Real social networks follow a power-law distribution. 
#    If the 'Degree Distribution' plot shows a sharp drop-off, the Reddit data 
#    is structurally sound for SNA analysis.
