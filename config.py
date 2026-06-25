"""Environment-backed configuration helpers."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def require_env(name: str) -> str:
    """Return a required environment variable or raise a clear error."""
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_int_env(name: str, default: int) -> int:
    """Read a positive integer environment variable."""
    value = os.getenv(name, str(default))
    try:
        parsed = int(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc
    if parsed <= 0:
        raise RuntimeError(f"{name} must be greater than zero")
    return parsed
