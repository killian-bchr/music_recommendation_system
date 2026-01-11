class MissingEnvironmentVariableError(Exception):
    """Raised when an expected environment variable is missing."""
    pass


class SpotifyClientInitializationError(Exception):
    """Raised when the Spotify client cannot be initialized."""
    pass
