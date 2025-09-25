import os
from music_engine.exceptions import MissingEnvironmentVariableError

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
        raise MissingEnvironmentVariableError(f"Missing environment variable: {name}")
    return value
