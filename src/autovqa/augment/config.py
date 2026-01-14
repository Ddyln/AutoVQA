import os
from pathlib import Path
from typing import Any, Dict, Optional

import tomli
from dotenv import load_dotenv
from loguru import logger
from platformdirs import user_config_dir

APP_NAME = "autovqa"
APP_AUTHOR = "autovqa"


def get_config_path() -> Path:
    """
    Get the path to the user's configuration file,
    including OpenAI-compatible APIs, generation settings, etc.

    Returns:
        Path to the config.toml file.
    """
    config_dir = user_config_dir(
        appname=APP_NAME,
        appauthor=APP_AUTHOR,
    )
    return Path(config_dir) / "config.toml"


def load_config() -> Dict[str, Any]:
    """
    Load the configuration from the config file.

    Returns:
        Configuration dictionary, or empty dict if file doesn't exist.
    """
    config_path = get_config_path()

    if not config_path.exists():
        logger.debug(f"Config file not found at: {config_path}")
        return {}

    try:
        with open(config_path, "rb") as f:
            return tomli.load(f)
    except tomli.TOMLDecodeError as e:
        logger.error(f"Invalid TOML format in {config_path}: {e}")
        raise ValueError(f"Invalid TOML format in config file {config_path}: {e}")
    except Exception as e:
        logger.error(f"Error reading config file {config_path}: {e}")
        raise ValueError(f"Error reading config file {config_path}: {e}")


def get_openai_api_key(service_name: Optional[str] = None) -> str:
    """
    Retrieve the OpenAI-compatable API key for the specified service.

    The function checks for the API key in the following order:
    1. Environment variables (via `.env` file or system environment)
    2. User configuration file (`config.toml`)

    User's `config.toml` config file should have the structure:
    ```
    [service_name]
    api_key = "your-key-here"
    ```

    Args:
        service_name: Name of the service (e.g., 'gemini', 'gpt', 'claude').
                     Defaults to 'gemini' if not provided.

    Returns:
        The API key as a string.

    Raises:
        ValueError: If the API key is not found in any location.
    """
    service_name = (service_name or "gemini").lower()
    logger.debug(f"Retrieving API key for service: {service_name}")

    load_dotenv()

    # Get API key from environment variable
    env_var_name = f"{service_name.upper()}_API_KEY"
    env_api_key = os.getenv(env_var_name)

    if env_api_key:
        logger.debug(f"Found API key in environment variable: {env_var_name}")
        return env_api_key

    logger.debug(f"Environment variable {env_var_name} not found, checking config file")

    config = load_config()
    config_path = get_config_path()

    if not config:
        raise ValueError(
            f"API key for '{service_name}' not found. "
            f"Please set the {env_var_name} environment variable or "
            f"create a config file at {config_path} with the following structure:\n\n"
            f"[{service_name}]\n"
            f'api_key = "your-key-here"'
        )

    # Check if service exists in config
    if service_name not in config:
        logger.debug(f"Service '{service_name}' not found in config file")
        config_path = get_config_path()
        raise ValueError(
            f"Service '{service_name}' not found in config file. "
            f"Please add a [{service_name}] section with an 'api_key' field"
            f"to {config_path}"
        )

    # Get API key from config file
    service_config = config.get(service_name, {})
    config_api_key = service_config.get("api_key")

    if config_api_key:
        logger.debug("Found API key in config file")
        return config_api_key

    logger.debug(f"Key 'api_key' not found in [{service_name}] section")
    raise ValueError(
        f"API key not found in [{service_name}] section of {config_path}. "
        f'Please add: api_key = "your-key-here"'
    )


def get_openai_generation_settings(
    service_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve the generation settings for the specified service.

    The function returns settings in the following priority order:
    1. User configuration file (config.toml)
    2. Default settings for the service

    User's `config.toml` config file should have the structure:
    ```
    [service_name]
    api_key = "your-key-here"
    model_name = "model-name"
    temperature = 1.0
    max_tokens = 2048
    ```

    Args:
        service_name: Name of the service (e.g., 'gemini', 'gpt', 'claude').
                     Defaults to 'gemini' if not provided.

    Returns:
        Dictionary containing generation settings.
    """

    service_name = (service_name or "gemini").lower()
    logger.debug(f"Retrieving generation settings for service: {service_name}")

    config = load_config()

    if service_name not in config:
        logger.debug(
            f"Service '{service_name}' not found in config file, ignoring settings."
            "It is advised to set generation settings in the config file,"
            "such as model_name, temperature, max_tokens:"
            " in the [{service_name}] section."
        )
        return {}

    settings = config.get(service_name, {})
    settings.pop("api_key", None)

    logger.debug(f"Loaded generation settings for {service_name}: {settings}")
    return settings


def get_qa_settings() -> Dict[str, Any]:
    config = load_config()
    config_path = get_config_path()

    if not config or "qa" not in config:
        logger.debug(
            f"'qa' section not found in config file {config_path}. "
            f"Please add a [qa] section with 'target_levels' field."
        )
        return {}

    qa_config = config.get("qa", {})
    return qa_config


if __name__ == "__main__":
    try:
        key = get_openai_api_key("Gemini")
        logger.info(f"API key retrieved successfully. Preview: {key[:4]}****")

        gen_settings = get_openai_generation_settings("Gemini")
        logger.info(f"Generation settings: {gen_settings}")

        qa_settings = get_qa_settings()
        logger.info(f"QA settings: {qa_settings}")

    except ValueError as e:
        logger.error(str(e))
