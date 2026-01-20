from dataclasses import dataclass

from models.node import Node
from models.relation import Relation


@dataclass
class Edge:
    u: Node
    v: Node
    relation: Relation
    weight: float
