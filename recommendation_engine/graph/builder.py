from typing import Optional, Tuple

import networkx as nx

from recommendation_engine.constants import NodeType
from recommendation_engine.edge import Edge
from recommendation_engine.mapping import AUTHORIZED_RELATIONS
from recommendation_engine.node import Node
from recommendation_engine.relation import Relation


class GraphBuilder:
    def __init__(self):
        self.G = nx.Graph()

    def build_node(self, node_type: NodeType, node_id: int) -> Node:
        if not isinstance(node_type, NodeType):
            raise TypeError("node_type must be NodeType")

        if not isinstance(node_id, int):
            raise TypeError("node_id must be int")

        return Node(node_type=node_type, node_id=node_id)

    def build_relation(self, u: Node, v: Node) -> Relation:
        if not isinstance(u, Node) or not isinstance(v, Node):
            raise TypeError("u and v must be Node instances")

        key = (u.node_type, v.node_type)
        if key in AUTHORIZED_RELATIONS:
            return AUTHORIZED_RELATIONS[key]

        rev_key = (v.node_type, u.node_type)
        if rev_key in AUTHORIZED_RELATIONS:
            return AUTHORIZED_RELATIONS[rev_key]

        raise ValueError(f"Forbidden relation between {u.node_type} and {v.node_type}")

    def build_edge(self, nodes: Tuple[Node, Node], weight: Optional[float]) -> Edge:
        u, v = nodes
        relation = self.build_relation(u, v)

        return Edge(
            u=u,
            v=v,
            relation=relation,
            weight=relation.default_weight if weight is None else weight,
        )

    def add_node(self, node: Node) -> None:
        if node.name in self.G:
            return

        self.G.add_node(
            node.name,
            type=node.node_type.value,
        )

    def add_edge(self, edge: Edge) -> None:
        self.G.add_edge(
            edge.u.name,
            edge.v.name,
            relation=edge.relation.name,
            weight=edge.weight,
        )
