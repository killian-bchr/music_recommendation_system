import pandas as pd
from pandas import DataFrame
from typing import Dict, List

from database.tables import AlbumORM, ArtistORM, TrackORM
from settings.namming import AlbumColumns, ArtistColumns, TrackColumns


class DataTransformer:

    @staticmethod
    def track_to_dict(track: TrackORM) -> Dict:
        return {
            TrackColumns.TRACK_ID: track.id,
            TrackColumns.ALBUM_ID: track.album_id,
            TrackColumns.RELEASE_DATE: track.album.release_date,
            TrackColumns.DURATION: track.duration,
            TrackColumns.POPULARITY: track.popularity,
            TrackColumns.LISTENERS: track.listeners,
            TrackColumns.PLAYCOUNT: track.playcount,
            TrackColumns.ARTIST_IDS: [artist.id for artist in track.artists]
        }

    @staticmethod
    def artist_to_dict(artist: ArtistORM) -> Dict:
        return {
            ArtistColumns.ARTIST_ID: artist.id,
            ArtistColumns.TAGS: [t.id for t in getattr(artist, "tags", [])],
            ArtistColumns.SIMILAR_ARTISTS: [a.id for a in getattr(artist, "similar_artists", [])]
        }

    @staticmethod
    def album_to_dict(album: AlbumORM) -> Dict:
        return {
            AlbumColumns.ALBUM_ID: album.id,
            AlbumColumns.RELEASE_DATE: album.release_date
        }

    @staticmethod
    def build_tracks_df(tracks: List[TrackORM]) -> DataFrame:
        df = pd.DataFrame([DataTransformer.track_to_dict(t) for t in tracks])
        df.set_index(TrackColumns.TRACK_ID, inplace=True)
        return df

    def build_artists_df(artists: List[ArtistORM]) -> DataFrame:
        df = pd.DataFrame([DataTransformer.artist_to_dict(a) for a in artists])
        df.set_index(ArtistColumns.ARTIST_ID, inplace=True)
        return df

    @staticmethod
    def build_track_artist_assoc_df(tracks: List[TrackORM]) -> DataFrame:
        rows = []
        for t in tracks:
            for a in t.artists:
                rows.append(
                    {TrackColumns.TRACK_ID: t.spotify_id, ArtistColumns.ARTIST_ID: a.spotify_id}
                )
        return pd.DataFrame(rows)
