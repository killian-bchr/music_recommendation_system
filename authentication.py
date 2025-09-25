import spotipy
from config import Config

from spotipy.oauth2 import SpotifyOAuth

SCOPE = "user-top-read user-read-private user-library-read playlist-read-private user-read-playback-state user-read-recently-played"


spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id = Config.CLIENT_ID_SPOTIFY,
    client_secret = Config.CLIENT_SECRET_SPOTIFY,
    redirect_uri = Config.REDIRECT_URI_SPOTIFY,
    scope = SCOPE,
))
