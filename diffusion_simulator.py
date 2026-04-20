import networkx as nx
import random
import pandas as pd

class DiffusionSimulator:
    """
    Stochastic simulation of information spread using 
    the Independent Cascade Model (ICM).
    """
    def __init__(self, graph):
        self.G = graph

    def run_icm(self, seed_nodes, p=0.1):
        """
        Runs a single cascade starting from seed_nodes.
        p: Probability of activation per edge.
        """
        active = set(seed_nodes)
        newly_active = list(seed_nodes)
        history = [len(active)]
        
        while newly_active:
            next_active = []
            for node in newly_active:
                for neighbor in self.G.neighbors(node):
                    if neighbor not in active:
                        # Probabilistic activation
                        if random.random() < p:
                            active.add(neighbor)
                            next_active.append(neighbor)
            newly_active = next_active
            history.append(len(active))
            
        return active, history

    def simulate_intervention(self, strategy='brokerage', p=0.1, n_seeds=5):
        """
        Compares different strategies for halting spread.
        - 'brokerage': Remove nodes with lowest Burt's Constraint.
        - 'popular': Remove nodes with highest Degree.
        """
        seeds = random.sample(list(self.G.nodes()), n_seeds)
        
        # 1. Baseline
        _, history_base = self.run_icm(seeds, p)
        
        # 2. Intervention
        G_pruned = self.G.copy()
        if strategy == 'brokerage':
            constraint = nx.constraint(self.G)
            # Remove top 5% brokers (lowest constraint)
            nodes_to_remove = sorted(constraint, key=constraint.get)[:int(len(self.G)*0.05)]
        else:
            degree = dict(self.G.degree())
            # Remove top 5% popular nodes
            nodes_to_remove = sorted(degree, key=degree.get, reverse=True)[:int(len(self.G)*0.05)]
            
        G_pruned.remove_nodes_from(nodes_to_remove)
        
        # Re-run simulation on pruned graph
        temp_sim = DiffusionSimulator(G_pruned)
        # Filter seeds that might have been removed
        remaining_seeds = [s for s in seeds if G_pruned.has_node(s)]
        _, history_int = temp_sim.run_icm(remaining_seeds, p)
        
        return history_base, history_int

# Explanation:
# 1. ICM is a 'Markovian' process where each neighbor has a one-shot activation probability.
# 2. Intervention: This simulates 'de-platforming' or 'information quarantine'. 
# 3. Core DS Insight: Removing brokers (low constraint) is often more effective at 
#    shattering information flow than removing popular nodes, because popular nodes 
#    tend to be redundant within clusters, while brokers are unique bridges.
