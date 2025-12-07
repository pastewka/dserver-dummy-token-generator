dserver-dummy-token-generator
=============================

**WARNING: This plugin is for DEVELOPMENT USE ONLY!**

A simple JWT token generator plugin for dserver that accepts any credentials
and generates valid JWT tokens. This is useful for development and testing
but should NEVER be used in production environments.

Installation
------------

Install the package::

    pip install -e .

Or add it to your development stack's requirements.

Configuration
-------------

Environment variables:

- ``DUMMY_TOKEN_EXPIRY_HOURS``: Token validity period in hours (default: 24)
- ``DUMMY_TOKEN_ACCEPT_ANY``: Accept any username/password (default: true)

Usage
-----

Once installed, the plugin adds a ``/token`` endpoint group to dserver:

Generate a token::

    curl -X POST http://localhost:5000/auth/token \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "anything"}'

Response::

    {"token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."}

Security Warning
----------------

This plugin:

- Accepts ANY username/password combination
- Does not validate credentials against any user database
- Generates tokens that are valid for the configured dserver instance

Use only in isolated development environments where security is not a concern.
