import logging
import pandas as pd
from pandas import DataFrame
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor, as_completed

from database.tables import AlbumORM, ArtistORM, TrackORM, ListeningORM
from models import Album, Artist, Tag, Track, Listening, Playlist, RawTrackData
from settings.namming import AlbumColumns, ArtistColumns, TrackColumns
from settings.constants import ArtistMethods, TrackMethods
from helpers import DBHelpers, SpotifyHelpers, LastFMHelpers

logger = logging.getLogger(__name__)


class DataTransformer:

    @staticmethod
    def track_to_dict(track: TrackORM) -> dict:
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
    def artist_to_dict(artist: ArtistORM) -> dict:
        return {
            ArtistColumns.ARTIST_ID: artist.id,
            ArtistColumns.TAGS: [t.id for t in getattr(artist, "tags", [])],
            ArtistColumns.SIMILAR_ARTISTS: [a.id for a in getattr(artist, "similar_artists", [])]
        }

    @staticmethod
    def album_to_dict(album: AlbumORM) -> dict:
        return {
            AlbumColumns.ALBUM_ID: album.id,
            AlbumColumns.RELEASE_DATE: album.release_date
        }

    @staticmethod
    def build_tracks_df(tracks: list[TrackORM]) -> DataFrame:
        df = pd.DataFrame([DataTransformer.track_to_dict(t) for t in tracks])
        df.set_index(TrackColumns.TRACK_ID, inplace=True)
        return df

    def build_artists_df(artists: list[ArtistORM]) -> DataFrame:
        df = pd.DataFrame([DataTransformer.artist_to_dict(a) for a in artists])
        df.set_index(ArtistColumns.ARTIST_ID, inplace=True)
        return df

    @staticmethod
    def build_track_artist_assoc_df(tracks: list[TrackORM]) -> DataFrame:
        rows = []
        for t in tracks:
            for a in t.artists:
                rows.append(
                    {TrackColumns.TRACK_ID: t.spotify_id, ArtistColumns.ARTIST_ID: a.spotify_id}
                )
        return pd.DataFrame(rows)

    @staticmethod
    def build_tag(tag_name: str) -> Tag:
        return Tag(
            name=tag_name
        )
    
    @staticmethod
    def build_tags(tag_names: list[str]) -> list[Tag]:
        return [DataTransformer.build_tag(tag_name) for tag_name in tag_names]

    @staticmethod
    def build_artist(artist_id: str, artist_name: str) -> Artist:
        return Artist(
            id=artist_id,
            name=artist_name
        )
    
    @staticmethod
    def build_artists(artists: dict[str, str]) -> list[Artist]:
        result=[]
        for artist_id, artist_name in artists.items():
            result.append(DataTransformer.build_artist(artist_id, artist_name))
        return result

    @staticmethod
    def build_album(raw_track: RawTrackData) -> Album:
        return Album(
            id=raw_track.album_id,
            name=raw_track.album_name,
            artists=DataTransformer.build_artists(raw_track.album_artists),
            release_date=raw_track.release_date,
            image_url=raw_track.image_url
        )

    @staticmethod
    def build_albums(raw_tracks: list[RawTrackData]) -> list[Album]:
        return [DataTransformer.build_album(r) for r in raw_tracks]

    @staticmethod
    def get_details_from_track(track_name, artist_name) -> dict:
        track_details = LastFMHelpers.get_track_details(
            track=track_name, 
            artist=artist_name,
            method=TrackMethods.TRACK_DETAILS.value
        )

        return track_details.get('track', {})

    @staticmethod
    def get_artist_details_from_artist(artist: Artist) -> dict:
        artist_details = LastFMHelpers.get_artist_details(
            artist=artist.name,
            method=ArtistMethods.ARTIST_DETAILS.value
        )

        if 'error' in artist_details:
            return {}
        
        return artist_details.get('artist', {})

    @staticmethod
    def get_similar_artists(artist_details: dict) -> list[Artist]:
        similar_artists = artist_details.get('similar', {}).get('artist', [])

        filtered_artists = {}
        for artist in similar_artists:
            artist_name = artist.get('name')
            artist_id = SpotifyHelpers.get_artist_id_from_name(artist_name)
            if artist_id:
                filtered_artists[artist_id]=artist_name

        return DataTransformer.build_artists(filtered_artists)

    @staticmethod
    def get_artist_tags(artist_details: dict) -> list[Tag]:
        tags = artist_details.get('tags', {}).get('tag', [])
        tag_names = [t.get('name') for t in tags]
        return DataTransformer.build_tags(tag_names)

    @staticmethod
    def fetch_artist_details(artist: Artist) -> Artist:
        artist_details = DataTransformer.get_artist_details_from_artist(artist)
        similar_artists = DataTransformer.get_similar_artists(artist_details)
        artist_tags = DataTransformer.get_artist_tags(artist_details)
        artist.similar_artists = similar_artists
        artist.tags = artist_tags
        return artist

    @staticmethod
    def build_raw_track_from_listening(listening: ListeningORM) -> RawTrackData:
        return RawTrackData(
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

    @staticmethod
    def build_raw_track_from_item(item: dict) -> RawTrackData:
        track=SpotifyHelpers.extract_track_from_item(item)
        album=SpotifyHelpers.extract_album_from_track(track)

        track_artists=SpotifyHelpers.extract_artists_from_json(track)
        album_artists=SpotifyHelpers.extract_artists_from_json(album)

        return RawTrackData(
            track_id=track.get('id'),
            track_name=track.get('name'),
            track_artists={a.get('id'): a.get('name') for a in track_artists},
            album_id=album.get('id'),
            album_name=album.get('name'),
            album_artists={a.get('id'): a.get('name') for a in album_artists},
            duration=track.get('duration_ms')/1000,
            popularity=int(track.get('popularity')),
            spotify_url=track.get('external_urls', {}).get('spotify'),
            release_date=SpotifyHelpers.parse_date(album.get('release_date')),
            image_url = SpotifyHelpers.get_album_image_url(album)
        )

    @staticmethod
    def build_track(raw_track: RawTrackData) -> Track:
        listeners = None
        playcount = None

        with ThreadPoolExecutor(max_workers=5) as executor:
            track_artist_name = next(iter(raw_track.track_artists.values()), None)
            future = executor.submit(
                DataTransformer.get_details_from_track,
                raw_track.track_name,
                track_artist_name
                )
            track_details = future.result()
            listeners = track_details.get('listeners')
            playcount = track_details.get('playcount')

        formatted_track = Track(
            id=raw_track.track_id,
            name=raw_track.track_name,
            artists=DataTransformer.build_artists(raw_track.track_artists),
            album=DataTransformer.build_album(raw_track),
            duration=raw_track.duration,
            popularity=raw_track.popularity,
            spotify_url=raw_track.spotify_url,
            listeners=listeners,
            playcount=playcount,
        )

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(
                    DataTransformer.fetch_artist_details, artist
                ) for artist in formatted_track.artists
            ]
            for future in as_completed(futures):
                future.result()

        return formatted_track

    @staticmethod
    def build_tracks(raw_tracks: list[RawTrackData]) -> list[Track]:
        tracks = []

        if not raw_tracks:
            return []

        max_workers = min(10, len(raw_tracks))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(DataTransformer.build_track, r) for r in raw_tracks]

            for future in as_completed(futures):
                try:
                    track = future.result()
                    tracks.append(track)
                except Exception as e:
                    logger.error(f"Error building a track : {e}")

        return tracks

    @staticmethod
    def build_playlist(playlist_id: str) -> Playlist:
        extracted_tracks = SpotifyHelpers.extract_tracks_from_playlist(
            playlist_id
        )

        raw_tracks = [DataTransformer.build_raw_track_from_item(t) for t in extracted_tracks]

        return Playlist(
            id = playlist_id,
            tracks = DataTransformer.build_tracks(raw_tracks)
        )

    @staticmethod
    def get_new_tracks(session: Session) -> list[Track]:
        existing_tracks = DBHelpers.get_all_tracks(session)
        existing_tracks_ids = [t.spotify_id for t in existing_tracks]

        existing_listenings = DBHelpers.get_all_listenings(session)

        tracks = []

        for listening in existing_listenings:
            if listening.track_id in existing_tracks_ids:
                continue
            raw_track = DataTransformer.build_raw_track_from_listening(listening)
            tracks.append(raw_track)

        return DataTransformer.build_tracks(tracks)

    @staticmethod
    def get_new_albums(session: Session) -> list[Album]:
        existing_albums = DBHelpers.get_all_albums(session)
        existing_albums_ids = [t.spotify_id for t in existing_albums]

        existing_listenings = DBHelpers.get_all_listenings(session)

        albums = []

        for listening in existing_listenings:
            if listening.album_id in existing_albums_ids:
                continue
            raw_track = DataTransformer.build_raw_track_from_listening(listening)
            albums.append(raw_track)

        return DataTransformer.build_albums(albums)

    @staticmethod
    def get_new_artists(session: Session) -> list[Artist]:
        existing_artists = DBHelpers.get_all_artists(session)
        existing_artists_ids = [a.spotify_id for a in existing_artists]

        existing_listenings = DBHelpers.get_all_listenings(session)

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

        return DataTransformer.build_artists(artists)

    @staticmethod
    def build_listening(item: dict) -> Listening:
        track=SpotifyHelpers.extract_track_from_item(item)
        album=SpotifyHelpers.extract_album_from_track(track)

        track_artists=SpotifyHelpers.extract_artists_from_json(track)
        album_artists=SpotifyHelpers.extract_artists_from_json(album)

        return Listening(
            played_at=SpotifyHelpers.parse_date(item.get('played_at')),
            track_id=track.get('id'),
            track_name=track.get('name'),
            track_artists={a.get('id'): a.get('name') for a in track_artists},
            album_id=album.get('id'),
            album_name=album.get('name'),
            album_artists={a.get('id'): a.get('name') for a in album_artists},
            duration=track.get('duration_ms')/1000,
            popularity=int(track.get('popularity')),
            spotify_url=track.get('external_urls', {}).get('spotify'),
            release_date=SpotifyHelpers.parse_date(album.get('release_date')),
            image_url = SpotifyHelpers.get_album_image_url(album)
        )

    @staticmethod
    def build_listenings(items: list[dict]) -> list[Listening]:
        listenings=[]
        for item in items:
            listenings.append(DataTransformer.build_listening(item))
        return listenings
