from dataclasses import dataclass


@dataclass(eq=True)
class RawTrackData:
    track_id: str
    track_name: str
    track_artists: dict[str, str]
    album_id: str
    album_name: str
    album_artists: dict[str, str]
    duration: float
    popularity: int
    spotify_url: str
    release_date: str
    image_url: str
