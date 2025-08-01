"""
Shared configuration loader for Tastytrade credentials.
This module provides a centralized way to load credentials from config.json.
"""

import json
import os


def load_config():
    """
    Load configuration from config.json file.

    Returns:
        dict: Configuration dictionary containing credentials and settings

    Raises:
        FileNotFoundError: If config.json is not found
        json.JSONDecodeError: If config.json is not valid JSON
        KeyError: If required credentials are missing from config
    """
    config_path = os.path.join(os.path.dirname(__file__), "config.json")

    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        # Validate that required keys exist
        if "tastytrade" not in config:
            raise KeyError("'tastytrade' section missing from config.json")

        tastytrade_config = config["tastytrade"]
        if "username" not in tastytrade_config or "password" not in tastytrade_config:
            raise KeyError("'username' or 'password' missing from tastytrade config")

        return config

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Config file not found at {config_path}. "
            "Please copy config.example.json to config.json and add your credentials."
        )


def get_tastytrade_credentials():
    """
    Get Tastytrade username and password from config.

    Returns:
        tuple: (username, password)
    """
    config = load_config()
    tastytrade_config = config["tastytrade"]
    return tastytrade_config["username"], tastytrade_config["password"]
