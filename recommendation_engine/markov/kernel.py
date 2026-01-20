from typing import Dict, List, Optional

import numpy as np
from networkx import Graph
from numpy import ndarray

from recommendation_engine.markov.node_index import NodeIndex
from settings.config_loader import load_markov_type_transition_matrix
from settings.constants import MarkovStrategy


class MarkovKernel:
    def __init__(self, G: Graph, strategy: Optional[MarkovStrategy] = None):
        self.G = G
        self.index = NodeIndex(self.G.nodes)

        self.strategy = strategy
        self.type_transition_matrix = load_markov_type_transition_matrix(self.strategy)

        self.P = np.zeros((self.index.n, self.index.n))

    def get_node_type(self, node: str) -> str:
        return self.G.nodes[node]["type"]

    def get_neighbors(self, node: str) -> List[str]:
        neighbors = list(self.G.neighbors(node))
        if len(neighbors) == 0:
            raise ValueError(f"Node {node} should have at least one neighbor!")

        return neighbors

    def group_neighbors_by_type(self, node: str) -> Dict[str, List[str]]:
        neighbors = self.get_neighbors(node)
        neighbors_by_type = {}

        for neigh in neighbors:
            neigh_type = self.get_node_type(neigh)
            neighbors_by_type.setdefault(neigh_type, []).append(neigh)

        return neighbors_by_type

    def normalize_type_probs(
        self,
        node_type: str,
        neighbors_by_type: Dict[str, List[str]],
    ) -> Dict[str, float]:
        raw_probs = {
            t: self.type_transition_matrix[node_type].get(t, 0.0)
            for t in neighbors_by_type
        }

        total = sum(raw_probs.values())

        if total == 0:
            return {}

        return {t: p / total for t, p in raw_probs.items()}

    def compute_neighbor_transition_probs(self, node: str) -> Dict[str, float]:
        node_type = self.get_node_type(node)
        neighbors_by_type = self.group_neighbors_by_type(node)
        type_probs = self.normalize_type_probs(node_type, neighbors_by_type)

        probs = {}

        for neigh_type, neighs in neighbors_by_type.items():
            type_prob = type_probs.get(neigh_type, 0.0)
            if type_prob == 0:
                continue

            proba_per_neighbor = type_prob / len(neighs)
            for neigh in neighs:
                probs[neigh] = proba_per_neighbor

        return probs

    def fill_transition_row(self, node: str) -> None:
        i = self.index.node_to_idx[node]
        probs = self.compute_neighbor_transition_probs(node)

        if not probs:
            self.P[i, i] = 1.0
            return

        for neigh, p in probs.items():
            j = self.index.node_to_idx[neigh]
            self.P[i, j] = p

    def validate_kernel(self, tol: float = 1e-8) -> None:
        if np.any(self.P < 0):
            raise ValueError("Negative probabilities detected")

        row_sums = self.P.sum(axis=1)
        for i, s in enumerate(row_sums):
            if s > 0 and abs(s - 1.0) > tol:
                raise ValueError(f"Row {i} sums to {s}, not 1")

    def build_kernel(self) -> ndarray:
        for node in self.index.nodes:
            self.fill_transition_row(node)

        self.validate_kernel()
        return self.P
