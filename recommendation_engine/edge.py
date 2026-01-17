from dataclasses import dataclass

from recommendation_engine.node import Node
from recommendation_engine.relation import Relation


@dataclass
class Edge:
    u: Node
    v: Node
    relation: Relation
    weight: float
