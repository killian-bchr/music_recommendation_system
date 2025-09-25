from datetime import datetime
from authentication import spotify_client as sp
from engine.models.track import Track


class SpotifyHelpers:

    @staticmethod
    def search_track(track: str, artist: str = None) -> dict:
        query = f"track:{track}"
        if artist:
            query += f" artist:{artist}"

        results = sp.search(q=query, type="track", limit=1)

        track = SpotifyHelpers.retrieve_track_searched(results)
        if not track:
            return None
        
        return SpotifyHelpers.format_track(track)

    @staticmethod
    def parse_release_date(date_str: str):
        formats = ["%Y-%m-%d", "%Y-%m", "%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    @staticmethod
    def retrieve_track_searched(results: dict) -> dict:
        if not results["tracks"]["items"]:
            return None

        return results["tracks"]["items"][0]
    
    @staticmethod
    def get_album_image_url(track: dict) -> str:
        album_images = track["album"]["images"]
        return album_images[1]["url"] if len(album_images) > 1 else album_images[0]["url"]

    @staticmethod
    def format_track(track: dict) -> Track:
        formated_track = Track(
            album_id = int(track["album"]["id"]),
            album_name = track["album"]["name"],
            release_date = SpotifyHelpers.parse_release_date(track["album"]['release_date']),
            album_artists_id = [int(artist["id"]) for artist in track["album"]["artists"]],
            album_artists_name = [artist["name"] for artist in track["album"]["artists"]],
            duration = track['duration_ms']/1000,
            track_id = int(track["id"]),
            track_name = track["name"],
            popularity = int(track["popularity"]),
            track_artists_id = [int(artist["id"]) for artist in track["artists"]],
            track_artists_name = [artist["name"] for artist in track["artists"]],
            image_url = SpotifyHelpers.get_album_image_url(track),
            spotify_url = track['external_urls']['spotify']
        )

        return formated_track