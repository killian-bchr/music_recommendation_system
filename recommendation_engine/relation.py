from dataclasses import dataclass

from constants import RelationType


@dataclass(frozen=True)
class Relation:
    name: RelationType
    default_weight: float = 1.0
