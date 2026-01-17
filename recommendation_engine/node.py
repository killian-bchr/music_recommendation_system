from dataclasses import dataclass

from recommendation_engine.constants import NodeType


@dataclass(frozen=True)
class Node:
    node_type: NodeType
    node_id: int

    @property
    def name(self) -> str:
        return f"{self.node_type.value}:{self.node_id}"  # noqa: E231
