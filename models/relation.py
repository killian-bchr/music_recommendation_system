from dataclasses import dataclass

from settings.constants import RelationType


@dataclass(frozen=True)
class Relation:
    name: RelationType
    default_weight: float = 1.0
