from typing import List, Optional
from datetime import datetime
from sqlalchemy import desc
from sqlalchemy.orm import joinedload, Session

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
    def fetch_all_listenings(session: Session) -> List[ListeningORM]:
        return session.query(ListeningORM).all()

    @staticmethod
    def fetch_last_listenings(
        session: Session, 
        n_listenings: int
    ) -> List[ListeningORM]:
        return (
            session.query(ListeningORM)
            .order_by(desc(ListeningORM.played_at))
            .limit(n_listenings)
            .all()
        )

    def get_tracks_by_spotify_ids(
        session: Session, 
        track_ids: List[str]
    ) -> List[TrackORM]:
        return (
            session.query(TrackORM)
            .filter(TrackORM.spotify_id.in_(track_ids))
            .all()
        )

    @staticmethod
    def fetch_last_tracks_listened(
        session: Session, 
        n_listenings: int
    ) -> List[TrackORM]:
        last_listenings = DBHelpers.fetch_last_listenings(session, n_listenings)
        track_ids = [l.track_id for l in last_listenings]
        return DBHelpers.get_tracks_by_spotify_ids(session, track_ids)

    @staticmethod
    def fetch_all_tracks(session: Session) -> List[TrackORM]:
        return (
            session.query(TrackORM)
            .options(
                joinedload(TrackORM.artists).joinedload(ArtistORM.tags),
                joinedload(TrackORM.artists).joinedload(ArtistORM.similar_artists),
                joinedload(TrackORM.album),
            )
            .all()
        )

    @staticmethod
    def fetch_all_albums(session: Session) -> List[AlbumORM]:
        return (
            session.query(AlbumORM)
            .options(
                joinedload(AlbumORM.artists),
            )
            .all()
        )

    @staticmethod
    def fetch_all_artists(session: Session) -> List[ArtistORM]:
        return (
            session.query(ArtistORM)
            .options(
                joinedload(ArtistORM.tags),
                joinedload(ArtistORM.similar_artists),
                joinedload(ArtistORM.albums),
            )
            .all()
        )

    @staticmethod
    def fetch_all_playlists(session: Session) -> List[PlaylistORM]:
        return session.query(PlaylistORM).all()

    @staticmethod
    def fetch_all_tags(session: Session) -> List[TagORM]:
        return (
            session.query(TagORM)
            .options(joinedload(TagORM.artists))
            .all()
        )

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
    def get_track_by_id(session: Session, track_id: int) -> Optional[TrackORM]:
        return session.query(TrackORM).filter_by(id=track_id).first()
