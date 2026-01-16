from sqlalchemy.orm import Session
from typing import List

from models import Album, Artist, Track
from helpers import DBHelpers
from preprocessing.data_builder import DataBuilder


class DataSelector:
    @staticmethod
    def select_new_tracks(session: Session) -> List[Track]:
        existing_tracks = DBHelpers.fetch_all_tracks(session)
        existing_tracks_ids = [t.spotify_id for t in existing_tracks]

        existing_listenings = DBHelpers.fetch_all_listenings(session)

        tracks = []

        for listening in existing_listenings:
            if listening.track_id in existing_tracks_ids:
                continue
            raw_track = DataBuilder.build_raw_track_from_listening(listening)
            tracks.append(raw_track)

        return DataBuilder.build_tracks(tracks)

    @staticmethod
    def select_new_albums(session: Session) -> List[Album]:
        existing_albums = DBHelpers.fetch_all_albums(session)
        existing_albums_ids = [t.spotify_id for t in existing_albums]

        existing_listenings = DBHelpers.fetch_all_listenings(session)

        albums = []

        for listening in existing_listenings:
            if listening.album_id in existing_albums_ids:
                continue
            raw_track = DataBuilder.build_raw_track_from_listening(listening)
            albums.append(raw_track)

        return DataBuilder.build_albums(albums)

    @staticmethod
    def select_new_artists(session: Session) -> List[Artist]:
        existing_artists = DBHelpers.fetch_all_artists(session)
        existing_artists_ids = [a.spotify_id for a in existing_artists]

        existing_listenings = DBHelpers.fetch_all_listenings(session)

        artists = {}

        for listening in existing_listenings:
            all_artists = {}
            if listening.track_artists:
                all_artists.update(listening.track_artists)
            if listening.album_artists:
                all_artists.update(listening.album_artists)

            for artist_id, artist_name in all_artists.items():
                if artist_id not in existing_artists_ids and artist_id not in artists:
                    artists[artist_id] = artist_name

        return DataBuilder.build_artists(artists)
