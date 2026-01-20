from typing import Any

from sqlalchemy.orm import Session

from database.tables import (
    AlbumORM,
    ArtistORM,
    ListeningORM,
    PlaylistORM,
    TagORM,
    TrackORM,
)
from helpers import DBHelpers
from models import Album, Artist, Listening, Playlist, Tag, Track


class CRUD:
    @staticmethod
    def save_object_to_session(session: Session, object: Any):
        session.add(object)
        session.flush()

    # TODO: Add a method with 'session.bulk_save_objects' !

    @staticmethod
    def listening_to_orm(session: Session, listening: Listening) -> ListeningORM:
        listening_db = DBHelpers.get_existing_listening(session, listening.played_at)
        if listening_db:
            return listening_db

        listenings_orm = ListeningORM(
            played_at=listening.played_at,
            track_id=listening.track_id,
            track_name=listening.track_name,
            track_artists=listening.track_artists,
            album_id=listening.album_id,
            album_name=listening.album_name,
            album_artists=listening.album_artists,
            duration=listening.duration,
            popularity=listening.popularity,
            spotify_url=listening.spotify_url,
            release_date=listening.release_date,
            image_url=listening.image_url,
        )
        CRUD.save_object_to_session(session, listenings_orm)
        return listenings_orm

    @staticmethod
    def listenings_to_orm(
        session: Session, listenings: list[Listening]
    ) -> list[ListeningORM]:
        return [CRUD.listening_to_orm(session, listening) for listening in listenings]

    @staticmethod
    def tag_to_orm(session: Session, tag: Tag) -> TagORM:
        tag_db = DBHelpers.get_existing_tag(session, tag.name)
        if tag_db:
            return tag_db

        tag_orm = TagORM(name=tag.name)
        CRUD.save_object_to_session(session, tag_orm)
        return tag_orm

    @staticmethod
    def album_to_orm(session: Session, album: Album) -> AlbumORM:
        album_db = DBHelpers.get_existing_album(session, album.id)

        if album_db:
            for artist in album.artists:
                artist_db = CRUD.artist_to_orm(session, artist)
                if artist_db not in album_db.artists:
                    album_db.artists.append(artist_db)
            return album_db

        album_orm = AlbumORM(
            spotify_id=album.id,
            name=album.name,
            release_date=album.release_date,
            image_url=album.image_url,
            artists=[CRUD.artist_to_orm(session, a) for a in album.artists],
        )
        CRUD.save_object_to_session(session, album_orm)
        return album_orm

    @staticmethod
    def albums_to_orm(session: Session, albums: list[Album]) -> list[AlbumORM]:
        return [CRUD.album_to_orm(session, a) for a in albums]

    @staticmethod
    def artist_to_orm(session: Session, artist: Artist, visited=None) -> ArtistORM:
        if visited is None:
            visited = set()

        if artist.id in visited:
            return None
        visited.add(artist.id)

        artist_db = DBHelpers.get_existing_artist(session, artist.id)
        if artist_db:
            if artist.tags:
                for tag in artist.tags:
                    tag_db = CRUD.tag_to_orm(session, tag)
                    if tag_db not in artist_db.tags:
                        artist_db.tags.append(tag_db)

            if artist.similar_artists:
                for sa in artist.similar_artists:
                    sa_db = CRUD.artist_to_orm(session, sa, visited)
                    if sa_db and sa_db not in artist_db.similar_artists:
                        artist_db.similar_artists.append(sa_db)

            return artist_db

        artist_orm = ArtistORM(spotify_id=artist.id, name=artist.name)

        CRUD.save_object_to_session(session, artist_orm)

        if artist_orm.tags:
            artist_orm.tags = [CRUD.tag_to_orm(session, tag) for tag in artist.tags]

        if artist_orm.similar_artists:
            artist_orm.similar_artists = [
                sa
                for sa in (
                    CRUD.artist_to_orm(session, sa, visited)
                    for sa in artist.similar_artists
                )
                if sa
            ]

        return artist_orm

    @staticmethod
    def artists_to_orm(session: Session, artists: list[Artist]) -> list[ArtistORM]:
        return [CRUD.artist_to_orm(session, a) for a in artists]

    @staticmethod
    def track_to_orm(session: Session, track: Track) -> TrackORM:
        track_db = DBHelpers.get_existing_track(session, track.id)
        if track_db:
            track_db.listeners = (
                track.listeners if track.listeners is not None else track_db.listeners
            )
            track_db.playcount = (
                track.playcount if track.playcount is not None else track_db.playcount
            )
            if track.artists:
                for artist in track.artists:
                    CRUD.artist_to_orm(session, artist)
            return track_db

        track_orm = TrackORM(
            spotify_id=track.id,
            name=track.name,
            duration=track.duration,
            popularity=track.popularity,
            spotify_url=track.spotify_url,
            image_url=track.image_url,
            listeners=track.listeners,
            playcount=track.playcount,
            album=CRUD.album_to_orm(session, track.album),
            artists=[CRUD.artist_to_orm(session, a) for a in track.artists],
        )

        CRUD.save_object_to_session(session, track_orm)
        return track_orm

    @staticmethod
    def tracks_to_orm(session: Session, tracks: list[Track]) -> list[TrackORM]:
        return [CRUD.track_to_orm(session, t) for t in tracks]

    @staticmethod
    def playlist_to_orm(session: Session, playlist: Playlist) -> PlaylistORM:
        playlist_db = DBHelpers.get_existing_playlist(session, playlist.id)
        if playlist_db:
            return playlist_db

        playlist_orm = PlaylistORM(
            spotify_id=playlist.id, tracks=CRUD.tracks_to_orm(session, playlist.tracks)
        )

        CRUD.save_object_to_session(session, playlist_orm)
        return playlist_orm

    @staticmethod
    def commit_session(session: Session) -> None:
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
