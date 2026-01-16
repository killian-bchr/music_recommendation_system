from typing import Dict, List

from models import Artist
from settings.constants import ArtistMethods, TrackMethods
from helpers import SpotifyHelpers, LastFMHelpers


class DataFetcher:
    @staticmethod
    def fetch_details_from_track(track_name: str, artist_name: str) -> Dict:
        track_details = LastFMHelpers.get_track_details(
            track=track_name, 
            artist=artist_name,
            method=TrackMethods.TRACK_DETAILS.value
        )

        return track_details.get('track', {})

    @staticmethod
    def fetch_artist_details_from_artist(artist: Artist) -> Dict:
        artist_details = LastFMHelpers.get_artist_details(
            artist=artist.name,
            method=ArtistMethods.ARTIST_DETAILS.value
        )

        if 'error' in artist_details:
            return {}
        
        return artist_details.get('artist', {})

    @staticmethod
    def fetch_similar_artists(artist_details: Dict) -> Dict:
        similar_artists = artist_details.get('similar', {}).get('artist', [])

        filtered_artists = {}
        for artist in similar_artists:
            artist_name = artist.get('name')
            artist_id = SpotifyHelpers.get_artist_id_from_name(artist_name)
            if artist_id:
                filtered_artists[artist_id]=artist_name

        return filtered_artists

    @staticmethod
    def fetch_artist_tags(artist_details: Dict) -> List[str]:
        tags = artist_details.get('tags', {}).get('tag', [])
        return [t.get('name') for t in tags]
