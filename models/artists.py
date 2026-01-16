from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from models.tags import Tag


@dataclass(eq=True)
class Artist:
    id: str
    name: str
    similar_artists: Optional[list["Artist"]] = None
    tags: Optional[list[Tag]] = None
