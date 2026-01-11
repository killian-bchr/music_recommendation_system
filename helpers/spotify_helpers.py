import logging
from datetime import datetime
from typing import Dict, List, Optional

from client import Client

sp_client = Client.get_spotify_client()
logger = logging.getLogger(__name__)


class SpotifyHelpers:

    @staticmethod
    def retrieve_track_searched(results: Dict) -> Dict:
        if not results["tracks"]["items"]:
            logger.warning(f"No results found")
            return None

        return results["tracks"]["items"][0]

    @staticmethod
    def extract_track_from_item(item: Dict) -> Dict:
        return item.get('track', {})

    @staticmethod
    def extract_album_from_track(track: Dict) -> Dict:
        return track.get('album', {})

    @staticmethod
    def extract_artists_from_json(data: Dict) -> List[Dict]:
        return data.get('artists', [])

    @staticmethod
    def parse_date(date_str: str) -> datetime:
        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%d",
            "%Y-%m",
            "%Y"
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
    
    @staticmethod
    def get_album_image_url(album_dict: Dict) -> str:
        album_images = album_dict.get('images')
        return album_images[1]["url"] if len(album_images) > 1 else album_images[0]["url"]

    @staticmethod
    def search_track(
        track: str,
        artist: str = None,
    ) -> Dict:
        query = f"track:{track}"
        if artist:
            query += f" artist:{artist}"

        try:
            results = sp_client.search(q=query, type="track", limit=1)
        except Exception as e:
            logger.error(f"Spotify API search error for query '{query}': {e}")
            return None

        return SpotifyHelpers.retrieve_track_searched(results)

    @staticmethod
    def get_artist_id_from_name(artist: str) -> Optional[str]:
        results = sp_client.search(q=f"artist:{artist}", type="artist", limit=1)
        items = results.get("artists", {}).get("items", [])
        if items:
            return items[0]["id"]
        return None

    @staticmethod
    def extract_tracks_from_playlist(playlist_id: str) -> List[Dict]:
        offset = 0

        all_tracks = []

        while True:
            response = sp_client.playlist_tracks(playlist_id, limit=100, offset=offset)

            tracks = response.get('items', [])
            all_tracks.extend(tracks)

            if len(tracks) < 100:
                break

            offset += 100
        
        return all_tracks

    @staticmethod
    def extract_tracks(nb_tracks: int) -> Dict:
        if nb_tracks <= 0 or nb_tracks > 50:
            raise ValueError(
                'The number of tracks to be extracted need to be between 1 and 50 !'
            )

        limit = min(50, nb_tracks)

        response = sp_client.current_user_recently_played(limit=limit)
        return response['items']
