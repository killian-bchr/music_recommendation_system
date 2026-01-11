from dataclasses import dataclass

from models.tracks import Track


@dataclass(eq=True)
class Playlist:
    id: str
    tracks: list[Track]
