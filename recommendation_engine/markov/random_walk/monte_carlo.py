from typing import List

import numpy as np
from numpy import ndarray

from recommendation_engine.markov.node_index import NodeIndex
from recommendation_engine.markov.random_walk.base import RandomWalkBase


class MonteCarloRW(RandomWalkBase):
    def __init__(
        self, P: ndarray, index: NodeIndex, seed_nodes: List[str], steps: int = 1000
    ):
        self.P = P
        self.index = index
        self.seed_nodes = seed_nodes
        self.steps = int(steps)

    def sample_random_walk(self, start_node: str) -> List[str]:
        current = start_node
        walk = [current]

        for _ in range(self.steps):
            neighbors_idx = np.where(self.P[self.index.node_to_idx[current], :] > 0)[0]
            probs = self.P[self.index.node_to_idx[current], neighbors_idx]
            probs /= probs.sum()
            current = self.index.idx_to_node[np.random.choice(neighbors_idx, p=probs)]
            walk.append(current)

        return walk

    def run(self) -> ndarray:
        counts = np.zeros(self.index.n)

        for start in self.seed_nodes:
            walk = self.sample_random_walk(start)

            for node in walk:
                counts[self.index.node_to_idx[node]] += 1

        return counts / counts.sum()
