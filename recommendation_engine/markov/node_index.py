from typing import List


class NodeIndex:
    def __init__(self, nodes: List[str]):
        self.nodes = nodes
        self.n = len(nodes)
        self.node_to_idx = {n: i for i, n in enumerate(nodes)}
        self.idx_to_node = {i: n for n, i in self.node_to_idx.items()}
