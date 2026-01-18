from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import networkx as nx
from networkx import Graph

from settings.mapping import NODE_COLORS, NODE_SIZES


class GraphVisualizer:
    @staticmethod
    def compute_layout(G: Graph, seed: int = 42) -> Dict:
        return nx.spring_layout(G, seed=seed)

    @staticmethod
    def build_node_colors(G: Graph) -> List:
        return [NODE_COLORS[G.nodes[n]["type"]] for n in G.nodes]

    @staticmethod
    def build_node_sizes(G: Graph, default: int = 80) -> List:
        return [NODE_SIZES.get(G.nodes[n]["type"], default) for n in G.nodes]

    @staticmethod
    def draw(
        G: Graph,
        pos: Dict,
        node_colors: List,
        node_sizes: List,
        edge_color: str = "lightgray",
        with_labels: bool = False,
        figsize: Tuple[int, int] = (12, 12),
    ) -> None:
        plt.figure(figsize=figsize)

        nx.draw(
            G,
            pos,
            node_color=node_colors,
            node_size=node_sizes,
            edge_color=edge_color,
            with_labels=with_labels,
        )

        plt.show()

    @staticmethod
    def visualize_graph(
        G: Graph,
        seed: int = 42,
        edge_color: str = "lightgray",
        with_labels: bool = False,
        figsize: Tuple[int, int] = (12, 12),
    ) -> None:
        pos = GraphVisualizer.compute_layout(G, seed)
        node_colors = GraphVisualizer.build_node_colors(G)
        node_sizes = GraphVisualizer.build_node_sizes(G)

        GraphVisualizer.draw(
            G,
            pos,
            node_colors,
            node_sizes,
            edge_color,
            with_labels,
            figsize,
        )

    @staticmethod
    def get_components(G: Graph) -> List[Dict]:
        return list(nx.connected_components(G))

    @staticmethod
    def get_number_of_components(G: Graph) -> int:
        components = GraphVisualizer.get_components(G)
        return len(components)

    @staticmethod
    def count_nodes(G: Graph) -> Dict[str, int]:
        count = {}

        for node_type in nx.get_node_attributes(G, "type").values():
            count[node_type] = count.get(node_type, 0) + 1

        return count
