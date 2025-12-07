"""
dserver-dummy-token-generator - Development-only JWT token generator for dserver.

WARNING: This plugin is intended for DEVELOPMENT USE ONLY!
It accepts any username/password combination and generates valid JWT tokens.
DO NOT use this in production environments.
"""

import logging
from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app, request, jsonify
from flask_smorest import Blueprint
from marshmallow import Schema, fields

from dservercore import ExtensionABC

from .config import Config, CONFIG_SECRETS_TO_OBFUSCATE


__version__ = "0.1.0"

logger = logging.getLogger(__name__)


# Schemas for API documentation
class TokenRequestSchema(Schema):
    """Schema for token request."""
    username = fields.String(required=True, metadata={"description": "Username"})
    password = fields.String(required=False, metadata={"description": "Password (ignored in development mode)"})


class TokenResponseSchema(Schema):
    """Schema for token response."""
    token = fields.String(required=True, metadata={"description": "JWT token"})


# Create the Flask-smorest blueprint
token_bp = Blueprint(
    "token",
    __name__,
    url_prefix="/auth",
    description="Development-only JWT token generator endpoints"
)


@token_bp.route("/token", methods=["POST"])
@token_bp.arguments(TokenRequestSchema)
@token_bp.response(200, TokenResponseSchema)
def get_token(request_data):
    """Generate a JWT token for development/testing.

    WARNING: This endpoint accepts ANY credentials in development mode.
    Do not use in production!

    The generated token is valid for 24 hours by default (configurable
    via DUMMY_TOKEN_EXPIRY_HOURS environment variable).
    """
    username = request_data.get("username", "admin")

    # In development mode, accept any credentials
    if not Config.DUMMY_TOKEN_ACCEPT_ANY:
        # Production mode would require actual authentication here
        logger.warning(
            "Token generation denied - DUMMY_TOKEN_ACCEPT_ANY is False"
        )
        return {"error": "Authentication not configured"}, 401

    # Get the private key from Flask app config (set by dservercore)
    private_key = current_app.config.get("JWT_PRIVATE_KEY")
    if not private_key:
        logger.error("JWT_PRIVATE_KEY not configured in Flask app")
        return {"error": "Server configuration error"}, 500

    # Create JWT token
    expiry_hours = Config.DUMMY_TOKEN_EXPIRY_HOURS
    payload = {
        "sub": username,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=expiry_hours),
        "fresh": True,
    }

    token = jwt.encode(payload, private_key, algorithm="RS256")

    logger.info(f"Generated token for user: {username} (expires in {expiry_hours}h)")

    return {"token": token}


class DummyTokenGeneratorExtension(ExtensionABC):
    """Development-only JWT token generator extension for dserver.

    WARNING: This extension is for DEVELOPMENT USE ONLY!
    It generates valid JWT tokens without proper authentication.

    Configuration (via environment variables):
    - DUMMY_TOKEN_EXPIRY_HOURS: Token validity period in hours (default: 24)
    - DUMMY_TOKEN_ACCEPT_ANY: Accept any credentials (default: true)
    """

    def init_app(self, app):
        """Initialize the extension with the Flask app."""
        # Log a prominent warning about development-only usage
        logger.warning(
            "\n"
            "=" * 70 + "\n"
            "  WARNING: Dummy Token Generator is ACTIVE!\n"
            "  This plugin accepts ANY credentials and generates valid tokens.\n"
            "  DO NOT use in production environments!\n"
            "=" * 70
        )

        app.config.setdefault(
            "DUMMY_TOKEN_EXPIRY_HOURS",
            Config.DUMMY_TOKEN_EXPIRY_HOURS
        )

        logger.info(
            f"DummyTokenGeneratorExtension initialized with "
            f"expiry={Config.DUMMY_TOKEN_EXPIRY_HOURS}h, "
            f"accept_any={Config.DUMMY_TOKEN_ACCEPT_ANY}"
        )

    def register_dataset(self, dataset_info):
        """Called when a dataset is registered - no action needed."""
        pass

    def get_config(self):
        """Return initial Config object."""
        return Config

    def get_config_secrets_to_obfuscate(self):
        """Return config secrets never to be exposed clear text."""
        return CONFIG_SECRETS_TO_OBFUSCATE

    def get_blueprint(self):
        """Return the Flask blueprint for this extension."""
        return token_bp
