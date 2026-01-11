from dataclasses import dataclass
from typing import Optional

from models.albums import Album
from models.artists import Artist


@dataclass(eq=True)
class Track:
    id: str
    name: str
    artists: list[Artist]
    album: Album
    duration: float
    popularity: int
    spotify_url: str
    listeners: Optional[int] = None
    playcount: Optional[int] = None
