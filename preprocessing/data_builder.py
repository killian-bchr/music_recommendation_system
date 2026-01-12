import logging
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed

from database.tables import ListeningORM
from models import Album, Artist, Tag, Track, Listening, Playlist, RawTrackData
from helpers import SpotifyHelpers
from preprocessing.data_fetcher import DataFetcher

logger = logging.getLogger(__name__)


class DataBuilder:
    @staticmethod
    def build_listening(item: Dict) -> Listening:
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
    def build_listenings(items: List[Dict]) -> List[Listening]:
        listenings=[]
        for item in items:
            listenings.append(DataBuilder.build_listening(item))
        return listenings

    @staticmethod
    def build_album(raw_track: RawTrackData) -> Album:
        return Album(
            id=raw_track.album_id,
            name=raw_track.album_name,
            artists=DataBuilder.build_artists(raw_track.album_artists),
            release_date=raw_track.release_date,
            image_url=raw_track.image_url
        )

    @staticmethod
    def build_albums(raw_tracks: List[RawTrackData]) -> List[Album]:
        return [DataBuilder.build_album(r) for r in raw_tracks]

    @staticmethod
    def build_artist(artist_id: str, artist_name: str) -> Artist:
        return Artist(
            id=artist_id,
            name=artist_name
        )
    
    @staticmethod
    def build_artists(artists: Dict[str, str]) -> List[Artist]:
        result=[]
        for artist_id, artist_name in artists.items():
            result.append(DataBuilder.build_artist(artist_id, artist_name))
        return result

    @staticmethod
    def build_tag(tag_name: str) -> Tag:
        return Tag(
            name=tag_name
        )
    
    @staticmethod
    def build_tags(tag_names: List[str]) -> List[Tag]:
        return [DataBuilder.build_tag(tag_name) for tag_name in tag_names]

    @staticmethod
    def update_artist_details(artist: Artist) -> Artist:
        artist_details = DataFetcher.fetch_artist_details_from_artist(artist)

        similar_artists_data = DataFetcher.fetch_similar_artists(artist_details)
        artist.similar_artists = DataBuilder.build_artists(similar_artists_data)

        artist_tags_data = DataFetcher.fetch_artist_tags(artist_details)
        artist.tags = DataBuilder.build_tags(artist_tags_data)

        return artist

    @staticmethod
    def build_track(raw_track: RawTrackData) -> Track:
        listeners = None
        playcount = None

        with ThreadPoolExecutor(max_workers=5) as executor:
            track_artist_name = next(iter(raw_track.track_artists.values()), None)
            future = executor.submit(
                DataFetcher.fetch_details_from_track,
                raw_track.track_name,
                track_artist_name
            )
            track_details = future.result()
            listeners = track_details.get('listeners')
            playcount = track_details.get('playcount')

        formatted_track = Track(
            id=raw_track.track_id,
            name=raw_track.track_name,
            artists=DataBuilder.build_artists(raw_track.track_artists),
            album=DataBuilder.build_album(raw_track),
            duration=raw_track.duration,
            popularity=raw_track.popularity,
            spotify_url=raw_track.spotify_url,
            listeners=listeners,
            playcount=playcount,
        )

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(
                    DataBuilder.update_artist_details, artist
                ) for artist in formatted_track.artists
            ]
            for future in as_completed(futures):
                future.result()

        return formatted_track

    @staticmethod
    def build_tracks(raw_tracks: List[RawTrackData]) -> List[Track]:
        tracks = []

        if not raw_tracks:
            return []

        max_workers = min(10, len(raw_tracks))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(DataBuilder.build_track, r) for r in raw_tracks]

            for future in as_completed(futures):
                try:
                    track = future.result()
                    tracks.append(track)
                except Exception as e:
                    logger.error(f"Error building a track : {e}")

        return tracks

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
    def build_raw_track_from_item(item: Dict) -> RawTrackData:
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
    def build_playlist(playlist_id: str) -> Playlist:
        extracted_tracks = SpotifyHelpers.extract_tracks_from_playlist(
            playlist_id
        )

        raw_tracks = [DataBuilder.build_raw_track_from_item(t) for t in extracted_tracks]

        return Playlist(
            id = playlist_id,
            tracks = DataBuilder.build_tracks(raw_tracks)
        )
