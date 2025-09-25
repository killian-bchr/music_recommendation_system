from dataclasses import dataclass
from datetime import datetime


@dataclass(eq=True, frozen=True)
class Track:
    album_id: int
    album_name: str
    release_date: datetime
    album_artists_id: list[int]
    album_artists_name: list[str]
    duration: float
    track_id: int
    track_name: str
    popularity: int
    track_artists_id: list[int]
    track_artists_name: list[str]
    image_url: str
    spotify_url: str
