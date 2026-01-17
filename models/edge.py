from dataclasses import dataclass

from models import Node, Relation


@dataclass
class Edge:
    u: Node
    v: Node
    relation: Relation
    weight: float
