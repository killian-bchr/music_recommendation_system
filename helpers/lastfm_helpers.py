import logging
from typing import Dict

import requests
from requests.exceptions import JSONDecodeError

from config import Config

logger = logging.getLogger(__name__)


class LastFMHelpers:
    API_KEY = Config.API_KEY_LAST_FM
    BASE_URL = "http://ws.audioscrobbler.com/2.0/?"

    @staticmethod
    def make_lastfm_request(params: Dict) -> Dict:
        """
        Helper method to make a GET request to the Last.fm API.

        Args:
            params: Query parameters for the API request.

        Returns:
            dict: Parsed JSON response as a dictionary if successful
                  (empty dictionary otherwise).
        """
        params["api_key"] = LastFMHelpers.API_KEY
        params["format"] = "json"

        response = requests.get(LastFMHelpers.BASE_URL, params=params)

        if response.status_code == 200:
            try:
                return response.json()

            except requests.RequestException as e:
                logger.error(f"HTTP error during Last.fm API call: {e}")
            except JSONDecodeError:
                logger.error(f"Failed to decode JSON response: {response.text}")

        else:
            logger.error(f"API Error: ' {response.status_code}, {response.text}")
            return {}

    @staticmethod
    def get_artist_details(artist: str, method: str) -> Dict:
        params = {
            "method": method,
            "artist": artist,
        }
        return LastFMHelpers.make_lastfm_request(params)

    @staticmethod
    def get_track_details(track: str, artist: str, method: str) -> Dict:
        params = {
            "method": method,
            "artist": artist,
            "track": track,
        }
        return LastFMHelpers.make_lastfm_request(params)
