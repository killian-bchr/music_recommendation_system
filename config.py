import os

from dotenv import load_dotenv

from exceptions.exceptions import MissingEnvironmentVariableError

load_dotenv("config.env")


class Config:
    @staticmethod
    def get_env_variable(name: str) -> str:
        """
        Retrieve the value of an environment variable.

        Args:
            name: The name of the environment variable to retrieve.

        Returns:
            str: The value of the environment variable.

        Raises:
            MissingEnvironmentVariableError: If the environment variable is missing.
        """
        value = os.getenv(name)
        if value is None:
            raise MissingEnvironmentVariableError(
                f"Missing environment variable: {name}"
            )
        return value

    API_KEY_LAST_FM = get_env_variable("API_KEY_LASTFM")
    CLIENT_SECRET_LAST_FM = get_env_variable("CLIENT_SECRET_LASTFM")
    CLIENT_ID_SPOTIFY = get_env_variable("CLIENT_ID_SPOTIFY")
    CLIENT_SECRET_SPOTIFY = get_env_variable("CLIENT_SECRET_SPOTIFY")
    REDIRECT_URI_SPOTIFY = get_env_variable("REDIRECT_URI_SPOTIFY")
    DATABASE_URL_PROD = get_env_variable("DATABASE_URL_PROD")
    DATABASE_URL_EXP = get_env_variable("DATABASE_URL_EXP")
    DATABASE_URL_TEST = get_env_variable("DATABASE_URL_TEST")
