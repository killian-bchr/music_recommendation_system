from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from database.tables import (
    AlbumORM,
    ArtistORM,
    TrackORM,
    ListeningORM,
    PlaylistORM,
    TagORM,
)


class DBHelpers:
    @staticmethod
    def get_all_listenings(session: Session) -> list[ListeningORM]:
        return session.query(ListeningORM).all()

    @staticmethod
    def get_all_tracks(session: Session) -> list[TrackORM]:
        return session.query(TrackORM).all()

    @staticmethod
    def get_all_albums(session: Session) -> list[AlbumORM]:
        return session.query(AlbumORM).all()

    @staticmethod
    def get_all_artists(session: Session) -> list[ArtistORM]:
        return session.query(ArtistORM).all()

    @staticmethod
    def get_all_playlists(session: Session) -> list[PlaylistORM]:
        return session.query(PlaylistORM).all()

    @staticmethod
    def get_existing_listening(session: Session, played_at: datetime) -> Optional[ListeningORM]:
        return session.query(ListeningORM).filter_by(played_at=played_at).first()

    @staticmethod
    def get_existing_tag(session: Session, tag_name: str) -> Optional[TagORM]:
        return session.query(TagORM).filter_by(name=tag_name).first()

    @staticmethod
    def get_existing_album(session: Session, spotify_id: str) -> Optional[AlbumORM]:
        return session.query(AlbumORM).filter_by(spotify_id=spotify_id).first()

    @staticmethod
    def get_existing_artist(session: Session, spotify_id: str) -> Optional[ArtistORM]:
        return session.query(ArtistORM).filter_by(spotify_id=spotify_id).first()

    @staticmethod
    def get_existing_track(session: Session, spotify_id: str) -> Optional[TrackORM]:
        return session.query(TrackORM).filter_by(spotify_id=spotify_id).first()

    @staticmethod
    def get_existing_playlist(session: Session, spotify_id: str) -> Optional[PlaylistORM]:
        return session.query(PlaylistORM).filter_by(spotify_id=spotify_id).first()

    @staticmethod
    def get_track_by_id(session: Session, track_id: int) -> TrackORM:
        return session.query(TrackORM).filter_by(id=track_id).first()
