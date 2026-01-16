from dataclasses import dataclass
from datetime import datetime


@dataclass(eq=True)
class Listening:
    played_at: datetime
    track_id: str
    track_name: str
    track_artists: dict
    album_id: str
    album_name: str
    album_artists: dict
    duration: float
    popularity: int
    spotify_url: str
    release_date: datetime
    image_url: str
