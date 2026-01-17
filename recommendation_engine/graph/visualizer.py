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
