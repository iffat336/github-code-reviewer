import pytest

from config import get_int_env, require_env


def test_require_env_rejects_missing_value(monkeypatch):
    monkeypatch.delenv("EXAMPLE_REQUIRED", raising=False)
    with pytest.raises(RuntimeError, match="EXAMPLE_REQUIRED"):
        require_env("EXAMPLE_REQUIRED")


def test_get_int_env_requires_positive_integer(monkeypatch):
    monkeypatch.setenv("LIMIT", "0")
    with pytest.raises(RuntimeError, match="greater than zero"):
        get_int_env("LIMIT", 10)
