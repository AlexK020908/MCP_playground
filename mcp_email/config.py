"""
Configuration for the email MCP. Base path is the directory containing the server (for credential paths).
"""
from __future__ import annotations

import os
from pathlib import Path

_BASE: Path | None = None


def set_base_path(path: Path) -> None:
    """Set the base path (e.g. project root) for resolving credential and output paths."""
    global _BASE
    _BASE = path.resolve()


def get_base_path() -> Path:
    """Return the base path. Must call set_base_path() first from the server."""
    if _BASE is None:
        raise RuntimeError("mcp_email.config: set_base_path() was not called")
    return _BASE


def get_gmail_cred_path() -> str:
    return os.environ.get("GMAIL_CREDENTIALS_JSON", str(get_base_path() / "gmail_credentials.json"))


def get_gmail_token_path() -> str:
    return os.environ.get("GMAIL_TOKEN_JSON", str(get_base_path() / "gmail_token.json"))


def get_outlook_cache_path() -> str:
    return os.environ.get("OUTLOOK_TOKEN_CACHE", str(get_base_path() / "outlook_token_cache.bin"))


def get_outlook_cache_2_path() -> str | None:
    return os.environ.get("OUTLOOK_TOKEN_CACHE_2")
