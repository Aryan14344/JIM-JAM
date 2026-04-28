import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

class SocialVisualizer:
    """
    Handles generation of plots for the SNA pipeline.
    """
    @staticmethod
    def plot_umap(projection_df, labels=None, filename="latent_map.png"):
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
        plt.savefig(filename)
        plt.close()

    @staticmethod
    def plot_diffusion_curve(history, filename="diffusion_curve.png"):
        """
        Plots the cumulative reach of information over time.
        """
        plt.figure(figsize=(10, 6))
        plt.plot(history, marker='o', linestyle='-', color='red')
        plt.title("Information Diffusion Cascade (Cumulative Reach)")
        plt.xlabel("Iteration (Hop Count)")
        plt.ylabel("Active Nodes")
        plt.grid(True)
        plt.savefig(filename)
        plt.close()

    @staticmethod
    def plot_degree_distribution(G, filename="degree_distribution.png"):
        """
        Visualizes the power-law signature of the network.
        """
        degrees = [d for n, d in G.degree()]
        plt.figure(figsize=(10, 6))
        plt.hist(degrees, bins=20, color='green', alpha=0.7)
        plt.title("Degree Distribution (Scale-Free Check)")
        plt.xlabel("Degree")
        plt.ylabel("Frequency")
        plt.savefig(filename)
        plt.close()

    @staticmethod
    def plot_similarity_heatmap(similarity_df):
        """
        Visualizes the overlap between subreddits as a heatmap.
        Improved to highlight subtle patterns by masking the diagonal.
        """
        import numpy as np
        data = similarity_df.values.copy()
        
        # 1. Mask the diagonal (identity) so it doesn't dominate the color scale
        np.fill_diagonal(data, 0)
        
        # 2. Determine a reasonable vmax for better contrast
        # We use the 98th percentile of non-zero values to make patterns "pop"
        flat_data = data.flatten()
        non_zero = flat_data[flat_data > 0]
        vmax = np.percentile(non_zero, 98) if len(non_zero) > 0 else 1.0
        
        plt.figure(figsize=(14, 12))
        img = plt.imshow(data, cmap='magma', interpolation='nearest', vmax=vmax)
        plt.colorbar(img, label='Jaccard Similarity (Weighted Contrast)')
        
        # Add labels
        ticks = range(len(similarity_df.columns))
        plt.xticks(ticks, similarity_df.columns, rotation=90, fontsize=7)
        plt.yticks(ticks, similarity_df.index, fontsize=7)
        
        plt.title("Subreddit Community Overlap Matrix (Diagonal Masked)")
        plt.tight_layout()
        plt.savefig("global_similarity_matrix.png", dpi=150)
        plt.close()

    @staticmethod
    def plot_global_sentiment(sentiment_list):
        """
        Plots a bar chart of average sentiment across subreddits.
        """
        subreddits = [x[0] for x in sentiment_list]
        scores = [x[1] for x in sentiment_list]
        
        plt.figure(figsize=(15, 6))
        colors = ['red' if s < 0 else 'green' for s in scores]
        plt.bar(subreddits, scores, color=colors, alpha=0.7)
        plt.axhline(0, color='black', linewidth=0.8)
        plt.xticks(rotation=90, fontsize=8)
        plt.title("Global Sentiment Landscape (Subreddit Averages)")
        plt.ylabel("Avg Sentiment Score")
        plt.tight_layout()
        plt.savefig("global_sentiment_landscape.png")
        plt.close()

# Explanation:
# 1. Non-Interactive Export: The visualizer saves to .png files, making it 
#    server-friendly for headless environments.
# 2. Power-Law Check: Real social networks follow a power-law distribution. 
#    If the 'Degree Distribution' plot shows a sharp drop-off, the Reddit data 
#    is structurally sound for SNA analysis.
