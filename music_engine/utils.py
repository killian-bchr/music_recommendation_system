import requests
import logging
from dotenv import load_dotenv
from json.decoder import JSONDecodeError
from typing import Any, Dict, Optional

import pandas as pd
from pandas import DataFrame

from music_engine.env_utils import get_env_variable
from music_engine.client import Client
from music_engine.constants import ArtistMethods, TrackMethods

load_dotenv("config.env")
logger = logging.getLogger(__name__)


class Utils:

    API_KEY_LASTFM = get_env_variable("API_KEY_LASTFM")
    BASE_URL = 'http://ws.audioscrobbler.com/2.0/?'
    sp_client = Client.get_spotify_client()

    base_params = {
        "api_key": API_KEY_LASTFM,
        "format": "json"
    }

    artist_details_cache = {}

    @staticmethod
    def make_lastfm_request(params: Dict[str, Any]) -> Dict:
        """
        Helper method to make a GET request to the Last.fm API.

        Args:
            params: Query parameters for the API request.

        Returns:
            Dict: Parsed JSON response as a dictionary if successful (empty dictionary otherwise).
        """
        try:
            response = requests.get(Utils.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"HTTP error during Last.fm API call: {e}")
        except JSONDecodeError:
            logger.error(f"Failed to decode JSON response: {response.text}")
        return {}

    @staticmethod
    def get_artist_details(artist_name: str, method: str) -> Dict:
        """
        Fetch artist-related information from the Last.fm API.

        Args:
            artist_name: Name of the artist.
            method: API method to call (e.g., 'artist.getSimilar').

        Returns:
            Optional[Dict]: JSON response from Last.fm API or empty dictionary if error occurs.
        """
        params = {
            "method": method,
            "artist": artist_name,
            **Utils.base_params
        }
        return Utils.make_lastfm_request(params)

    @staticmethod
    def get_track_details(track_name: str, method: str, artist_name: Optional[str]) -> Dict:
        """
        Fetch track-related information from the Last.fm API.

        Args:
            track_name: Name of the track.
            method: API method to call (e.g., 'track.getInfo').
            artist_name (Optional): Name of the artist, optional but recommended.

        Returns:
            Optional[Dict]: JSON response from Last.fm API or empty dictionary if error occurs.
        """
        params = {
            "method": method,
            "track": track_name,
            **Utils.base_params
        }
        if artist_name:
            params["artist"] = artist_name

        return Utils.make_lastfm_request(params)

    @staticmethod
    def search_track(track_name: str, artist_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Search for a track on Spotify.

        Args:
            track_name: Name of the track to search for.
            artist_name (Optional): Name of the artist, optional but recommended.

        Returns:
            Optional[Dict[str, Any]]: Dictionary with track features if found, None otherwise.
        """
        query = f"track:{track_name}"
        if artist_name:
            query += f" artist:{artist_name}"

        try:
            results = Utils.sp_client.search(q=query, type="track", limit=1)
        except Exception as e:
            logger.error(f"Spotify API search error for query '{query}': {e}")
            return None

        if results["tracks"]["items"]:
            track = results["tracks"]["items"][0]

            album_images = track["album"]["images"]
            album_image_url = album_images[1]["url"] if len(album_images) > 1 else album_images[0]["url"]
            
            return {
                "album_id": track["album"]["id"],
                "album_name": track["album"]["name"],
                "release_date": track["album"]["release_date"],
                "album_artists_id": ", ".join(str(artist["id"]) for artist in track["album"]["artists"]),
                "album_artists_name": ", ".join(artist["name"] for artist in track["album"]["artists"]),
                "duration": track['duration_ms']/1000,
                "track_id": track["id"],
                "track_name": track["name"],
                "popularity": track["popularity"],
                "track_artists_id": ", ".join(str(artist["id"]) for artist in track["artists"]),
                "track_artists_name": ", ".join(artist["name"] for artist in track["artists"]),
                'image_url': album_image_url,
                'spotify_url': track['external_urls']['spotify']
            }
        else:
            logger.warning(f"No results found for query '{query}'")
            return None

    @staticmethod
    def extract_track_info(track: Dict) -> Dict:
        """
        Extracts key information from a Spotify track dictionary.

        Args:
            track: A dictionary representing a Spotify track object.

        Returns:
            Dict: A dictionary containing extracted information such as album details,
                  track duration (in seconds), track and album artists (IDs and names),
                  popularity, album image URL, and Spotify URL.
        """
        album_images = track['album']['images']
        album_image_url = album_images[1]['url'] if len(album_images) > 1 else album_images[0]['url'] if album_images else None
        return {
            'album_id': track['album']['id'],
            'album_name': track['album']['name'],
            'release_date': track['album']['release_date'],
            'album_artists_id': ', '.join([artist['id'] for artist in track['album']['artists']]),
            'album_artists_name': ', '.join([artist['name'] for artist in track['album']['artists']]),
            'duration': track['duration_ms'] / 1000,
            'track_id': track['id'],
            'track_name': track['name'],
            'popularity': track['popularity'],
            'track_artists_id': ', '.join([artist['id'] for artist in track['artists']]),
            'track_artists_name': ', '.join([artist['name'] for artist in track['artists']]),
            'image_url': album_image_url,
            'spotify_url': track['external_urls']['spotify']
        }

    @staticmethod
    def extract_track_details(track_name: str, artist_name: str) -> Optional[Dict]:
        """
        Retrieves detailed metadata for a specific track using its name and artist.

        Args:
            track_name: The name of the track.
            artist_name: The name of the track's main artist.

        Returns:
            Optional[Dict]: A dictionary with detailed track information if found,
                            otherwise None.
        """
        details = Utils.get_track_details(track_name=track_name, artist_name=artist_name, method=TrackMethods.INFO)
        if not details or 'track' not in details:
            logger.warning(f"No further details found")
            return None
        return details.get('track')

    @staticmethod
    def extract_similar_artists_and_tags(artists_names: list[str]) -> Dict[str, str]:
        """
        Fetches similar artists and associated tags for a list of artist names.

        Args:
            artists_names: A list of artist names to retrieve data for.

        Returns:
            Dict[str, str]: A dictionary with two optional keys:
                - "similar_artists": Comma-separated string of similar artist names.
                - "track_tags": Comma-separated string of tags associated with the artists.
                Keys are present only if data is found.

        Note:
            This function uses an internal cache to store artist details once fetched.
            When querying data for an artist, it first checks the cache to avoid 
            redundant API calls, which improves efficiency and reduces the load on external services.
            """
        similar_artists = []
        track_tags = []

        for artist_name in artists_names:
            if artist_name in Utils.artist_details_cache:
                artist_details = Utils.artist_details_cache[artist_name]
            else:
                artist_details = Utils.get_artist_details(
                    artist_name=artist_name,
                    method=ArtistMethods.INFO
                )
                Utils.artist_details_cache[artist_name] = artist_details

            if artist_details and "error" not in artist_details:
                similar = artist_details.get('artist', {}).get('similar', {}).get('artist', [])
                similar_artists.extend([a['name'] for a in similar])

                tag_list = artist_details.get('artist', {}).get('tags', {}).get('tag', [])
                track_tags.extend([tag['name'] for tag in tag_list])

            else:
                logger.warning(f"No similar artists neither track tags found for {artist_name}")

        similar_artists_str = ", ".join(set(similar_artists))
        track_tags_str = ", ".join(set(track_tags))

        result = {}
        if len(similar_artists_str)>0:
            result["similar_artists"] = similar_artists_str
        if len(track_tags_str)>0:
            result["track_tags"] = track_tags_str

        return result

    @staticmethod
    def get_playlist_tracks(playlist_id: str) -> DataFrame:
        """
        Retrieves all tracks from a Spotify playlist and compiles their metadata into a DataFrame.

        Args:
            playlist_id: The Spotify ID of the playlist.

        Returns:
            pd.DataFrame: A DataFrame where each row corresponds to a track with columns
                          including album info, track info, popularity, listeners count,
                          playcount, similar artists, tags, and release date as datetime.
        """
        tracks = []
        offset = 0

        while True:
            response = Utils.sp_client.playlist_tracks(playlist_id, limit=100, offset=offset)
            items = response.get('items', [])
            
            for item in items:
                track = item['track']
                track_infos = Utils.extract_track_info(track)

                track_details = Utils.extract_track_details(
                    track['name'],
                    track['artists'][0]['name']
                )

                artists_names = [artist['name'] for artist in track['artists']]
                result = Utils.extract_similar_artists_and_tags(artists_names)

                complete_track = {
                    **track_infos,
                    'track_listeners': track_details.get('listeners', None),
                    'track_playcount': track_details.get('playcount', None),
                    'similar_artists': result.get('similar_artists', None),
                    'track_tags': result.get('track_tags', None),
                }

                tracks.append(complete_track)
                    
            
            if len(items) < 100:
                break

            offset += 100

        playlist = pd.DataFrame(tracks)
        playlist['release_date'] = pd.to_datetime(playlist['release_date'], errors='coerce')

        return playlist

    @staticmethod
    def get_recent_tracks(numbers: int) -> DataFrame:
        """
        Retrieves the most recent tracks played by the current user, along with detailed information for each track.

        Args:
            numbers: The number of last tracks to retrieve. Must be less than or equal to 50, 
                     as the API limits the maximum number of recently played tracks returned.

        Returns:
            pd.DataFrame: A DataFrame containing information on the recently played tracks, including:
                - Album details (id, name, release date, artists)
                - Track details (id, name, duration, popularity, artists)
                - Additional metadata such as track listeners, playcount, similar artists, and tags
                - Timestamp of when the track was played ('played_at')
                - URLs for album art and Spotify track link
        """
        limit = min(50, numbers)
        response = Utils.sp_client.current_user_recently_played(limit=limit)
        items = response.get('items', [])

        all_tracks = []

        for item in items:
            track = item['track']
            track_infos = Utils.extract_track_info(track)

            track_details = Utils.extract_track_details(
                track['name'],
                track['artists'][0]['name']
            )

            artists_names = [artist['name'] for artist in track['artists']]
            result = Utils.extract_similar_artists_and_tags(artists_names)

            complete_track = {
                **track_infos,
                'played_at': item['played_at'],
                'track_listeners': track_details.get('listeners', None),
                'track_playcount': track_details.get('playcount', None),
                'similar_artists': result.get('similar_artists', None),
                'track_tags': result.get('track_tags', None),
            }

            all_tracks.append(complete_track)

        recent_tracks_df = pd.DataFrame(all_tracks)
        recent_tracks_df.reset_index(inplace=True, drop=True)
        recent_tracks_df['release_date'] = pd.to_datetime(recent_tracks_df['release_date'], errors='coerce')
        recent_tracks_df['played_at'] = pd.to_datetime(recent_tracks_df['played_at'], errors='coerce')

        return recent_tracks_df
