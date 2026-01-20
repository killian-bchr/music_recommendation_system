from typing import List

import numpy as np
from numpy import ndarray

from recommendation_engine.markov.node_index import NodeIndex


class InitialDistributionBuilder:
    def __init__(self, seed_nodes: List[str], index: NodeIndex):
        self.index = index
        self.seed_nodes = seed_nodes

    def get_valid_seeds(self) -> List[str]:
        valid_seeds = [n for n in self.seed_nodes if n in self.index.node_to_idx.keys()]
        if not valid_seeds:
            raise ValueError("No seed nodes found in graph")

        return valid_seeds

    def build(self) -> ndarray:
        pi0 = np.zeros(self.index.n)

        valid_seeds = self.get_valid_seeds()

        for node in valid_seeds:
            pi0[self.index.node_to_idx[node]] = 1.0 / len(valid_seeds)

        return pi0
