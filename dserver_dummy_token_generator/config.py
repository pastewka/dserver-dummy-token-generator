"""Configuration for the dummy token generator plugin."""

import os


class Config:
    """Configuration loaded from environment variables."""

    # Token expiry time in hours (default: 24 hours)
    DUMMY_TOKEN_EXPIRY_HOURS = int(
        os.environ.get("DUMMY_TOKEN_EXPIRY_HOURS", "24")
    )

    # Whether to accept any credentials (development mode)
    # WARNING: This should ONLY be True in development environments!
    DUMMY_TOKEN_ACCEPT_ANY = os.environ.get(
        "DUMMY_TOKEN_ACCEPT_ANY", "true"
    ).lower() in ("true", "1", "yes")


# No secrets to obfuscate for this plugin
CONFIG_SECRETS_TO_OBFUSCATE = []
