from datetime import datetime

from dataclasses import dataclass
from models.artists import Artist


@dataclass(eq=True)
class Album:
    id: str
    name: str
    artists: list[Artist]
    release_date: datetime
    image_url: str
