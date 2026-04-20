import networkx as nx
import pandas as pd
from sklearn.preprocessing import StandardScaler

class AntiFluffEngine:
    """
    Data Science Preprocessing for Social Graphs.
    Handles noise reduction via quantiles and feature normalization.
    """
    def __init__(self, interaction_df):
        self.df = interaction_df
        self.G = self._build_initial_graph()

    def _build_initial_graph(self):
        G = nx.from_pandas_edgelist(
            self.df, 'source', 'target', 
            edge_attr=['weight', 'timestamp'],
            create_using=nx.DiGraph()
        )
        return G

    def prune_edges(self, q=0.75):
        """
        Removes edges below the q-th quantile of weight.
        Ensures we only model 'significant' interactions.
        """
        weights = pd.Series([d['weight'] for u, v, d in self.G.edges(data=True)])
        threshold = weights.quantile(q)
        
        print(f"[*] Pruning edges with weight < {threshold} (Quantile: {q})")
        
        to_remove = [
            (u, v) for u, v, d in self.G.edges(data=True) 
            if d['weight'] < threshold
        ]
        
        self.G.remove_edges_from(to_remove)
        # Remove isolated nodes (nodes with no connections after pruning)
        self.G.remove_nodes_from(list(nx.isolates(self.G)))
        
        return self.G

    def scale_node_features(self):
        """
        Normalizes node metadata (centrality, etc.) for embedding stability.
        """
        degrees = dict(self.G.degree())
        betweenness = nx.betweenness_centrality(self.G)
        
        features_df = pd.DataFrame({
            'degree': list(degrees.values()),
            'betweenness': list(betweenness.values())
        }, index=list(degrees.keys()))
        
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features_df)
        
        return pd.DataFrame(scaled_features, columns=features_df.columns, index=features_df.index)

# Explanation:
# 1. We transform the Reddit CSV/DataFrame into a Directed Graph (DiGraph).
# 2. We use Pandas.quantile() to find the statistical cut-off for interaction intensity.
# 3. We use StandardScaler to ensure that 'popular' nodes don't have numerically 
#    unfair weight over 'strategic' nodes during the Dimensionality Reduction phase.
