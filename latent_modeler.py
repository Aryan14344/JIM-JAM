from node2vec import Node2Vec
import umap
import pandas as pd
import numpy as np

class LatentModeler:
    """
    Handles High-Dimensional Graph Embeddings and 
    Manifold Learning (UMAP) for latent pattern discovery.
    """
    def __init__(self, graph):
        self.G = graph
        self.model = None
        self.embeddings = None

    def generate_embeddings(self, dimensions=64, walk_length=30, num_walks=100):
        """
        Uses Node2Vec to learn user behavioral patterns.
        """
        print(f"[*] Generating {dimensions}-d latent embeddings using Node2Vec...")
        # Higher walk_length captures global structure, lower captures local neighborhoods.
        n2v = Node2Vec(self.G, dimensions=dimensions, walk_length=walk_length, num_walks=num_walks)
        self.model = n2v.fit(window=10, min_count=1, batch_words=4)
        
        # Extract vectors
        self.embeddings = {node: self.model.wv[node] for node in self.G.nodes()}
        return self.embeddings

    def project_to_2d(self):
        """
        Non-linear dimensionality reduction using UMAP to visualize interaction clusters.
        """
        print("[*] Projecting embeddings into 2D using UMAP...")
        nodes = list(self.embeddings.keys())
        vectors = np.array([self.embeddings[node] for node in nodes])
        
        reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, metric='cosine')
        u_map = reducer.fit_transform(vectors)
        
        return pd.DataFrame(u_map, columns=['UMAP_1', 'UMAP_2'], index=nodes)

# Explanation:
# 1. Node2Vec works by simulating 'random walks' through the graph. 
#    Users that appear in similar walk sequences are given similar vectors.
# 2. UMAP (Uniform Manifold Approximation and Projection) is superior to t-SNE 
#    because it preserves the global relationship between clusters better.
# 3. Use Case: If two users are in the same UMAP cluster but share no common subreddits, 
#    we have discovered a 'latent synchronization' in their social behavior.
