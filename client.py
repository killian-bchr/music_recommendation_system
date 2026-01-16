import spotipy
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

from config import Config
from exceptions.exceptions import SpotifyClientInitializationError

load_dotenv("config.env")


class Client:
    CLIENT_ID_SPOTIFY = Config.CLIENT_ID_SPOTIFY
    CLIENT_SECRET_SPOTIFY = Config.CLIENT_SECRET_SPOTIFY
    REDIRECT_URI_SPOTIFY = Config.REDIRECT_URI_SPOTIFY
    SCOPE = " ".join(
        [
            "user-top-read",
            "user-read-private",
            "user-library-read",
            "playlist-read-private",
            "user-read-playback-state",
            "user-read-recently-played",
        ]
    )

    @staticmethod
    def get_spotify_client() -> Spotify:
        """
        Initialize and return a Spotify client using Spotipy and OAuth authentication.

        This method authenticates the user via SpotifyOAuth and returns a Spotipy client
        instance to interact with the Spotify Web API.

        Returns:
            Spotify: An authenticated Spotipy client instance.

        Raises:
            SpotifyClientInitializationError: If the Spotify client fails to initialize.
        """
        try:
            return spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=Client.CLIENT_ID_SPOTIFY,
                    client_secret=Client.CLIENT_SECRET_SPOTIFY,
                    redirect_uri=Client.REDIRECT_URI_SPOTIFY,
                    scope=Client.SCOPE,
                )
            )

        except Exception as e:
            raise SpotifyClientInitializationError(
                f"Failed to initialize Spotify client: {e}"
            )
