"""Tests for envspec.get()."""

import pytest

import envspec
from envspec import EnvCastError, EnvValidationError


# ---------------------------------------------------------------------------
# Basic retrieval
# ---------------------------------------------------------------------------

def test_get_raw_string(monkeypatch):
    monkeypatch.setenv("MY_VAR", "hello")
    assert envspec.get("MY_VAR") == "hello"


def test_get_returns_default_when_missing(monkeypatch):
    monkeypatch.delenv("MISSING_VAR", raising=False)
    assert envspec.get("MISSING_VAR", default=42) == 42


def test_get_default_none(monkeypatch):
    monkeypatch.delenv("MISSING_VAR", raising=False)
    assert envspec.get("MISSING_VAR", default=None) is None


def test_get_required_missing_raises(monkeypatch):
    monkeypatch.delenv("REQUIRED_VAR", raising=False)
    with pytest.raises(EnvCastError, match="Required variable REQUIRED_VAR is not set"):
        envspec.get("REQUIRED_VAR")


def test_get_required_missing_hint_in_message(monkeypatch):
    monkeypatch.delenv("DB_URL", raising=False)
    with pytest.raises(EnvCastError, match="Add DB_URL"):
        envspec.get("DB_URL")


# ---------------------------------------------------------------------------
# int casting
# ---------------------------------------------------------------------------

def test_get_int(monkeypatch):
    monkeypatch.setenv("PORT", "8080")
    assert envspec.get("PORT", cast=int) == 8080


def test_get_int_negative(monkeypatch):
    monkeypatch.setenv("OFFSET", "-1")
    assert envspec.get("OFFSET", cast=int) == -1


def test_get_int_invalid_raises(monkeypatch):
    monkeypatch.setenv("PORT", "abc")
    with pytest.raises(EnvCastError, match='Cannot cast PORT='):
        envspec.get("PORT", cast=int)


# ---------------------------------------------------------------------------
# float casting
# ---------------------------------------------------------------------------

def test_get_float(monkeypatch):
    monkeypatch.setenv("TIMEOUT", "30.5")
    assert envspec.get("TIMEOUT", cast=float) == 30.5


def test_get_float_integer_string(monkeypatch):
    monkeypatch.setenv("TIMEOUT", "30")
    assert envspec.get("TIMEOUT", cast=float) == 30.0


def test_get_float_invalid_raises(monkeypatch):
    monkeypatch.setenv("TIMEOUT", "fast")
    with pytest.raises(EnvCastError, match="Cannot cast TIMEOUT="):
        envspec.get("TIMEOUT", cast=float)


# ---------------------------------------------------------------------------
# bool casting
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", ["1", "true", "True", "TRUE", "yes", "YES", "on", "ON"])
def test_get_bool_truthy(monkeypatch, raw):
    monkeypatch.setenv("DEBUG", raw)
    assert envspec.get("DEBUG", cast=bool) is True


@pytest.mark.parametrize("raw", ["0", "false", "False", "FALSE", "no", "NO", "off", "OFF"])
def test_get_bool_falsy(monkeypatch, raw):
    monkeypatch.setenv("DEBUG", raw)
    assert envspec.get("DEBUG", cast=bool) is False


def test_get_bool_invalid_raises(monkeypatch):
    monkeypatch.setenv("DEBUG", "maybe")
    with pytest.raises(EnvCastError, match="Cannot cast DEBUG="):
        envspec.get("DEBUG", cast=bool)


# ---------------------------------------------------------------------------
# str casting
# ---------------------------------------------------------------------------

def test_get_str_cast(monkeypatch):
    monkeypatch.setenv("NAME", "alice")
    assert envspec.get("NAME", cast=str) == "alice"


# ---------------------------------------------------------------------------
# list casting
# ---------------------------------------------------------------------------

def test_get_list_of_strings(monkeypatch):
    monkeypatch.setenv("HOSTS", "a,b,c")
    assert envspec.get("HOSTS", cast=list) == ["a", "b", "c"]


def test_get_list_strips_whitespace(monkeypatch):
    monkeypatch.setenv("HOSTS", "a , b , c")
    assert envspec.get("HOSTS", cast=list) == ["a", "b", "c"]


def test_get_list_empty_string(monkeypatch):
    monkeypatch.setenv("HOSTS", "")
    assert envspec.get("HOSTS", cast=list) == []


def test_get_list_int(monkeypatch):
    monkeypatch.setenv("PORTS", "80,443,8080")
    assert envspec.get("PORTS", cast=list[int]) == [80, 443, 8080]


def test_get_list_float(monkeypatch):
    monkeypatch.setenv("WEIGHTS", "0.1,0.9")
    assert envspec.get("WEIGHTS", cast=list[float]) == [0.1, 0.9]


def test_get_list_str(monkeypatch):
    monkeypatch.setenv("NAMES", "alice,bob")
    assert envspec.get("NAMES", cast=list[str]) == ["alice", "bob"]


def test_get_list_int_invalid_raises(monkeypatch):
    monkeypatch.setenv("PORTS", "80,abc")
    with pytest.raises(EnvCastError):
        envspec.get("PORTS", cast=list[int])


# ---------------------------------------------------------------------------
# Path casting
# ---------------------------------------------------------------------------

def test_get_path(monkeypatch, tmp_path):
    from pathlib import Path
    monkeypatch.setenv("LOG_DIR", str(tmp_path))
    result = envspec.get("LOG_DIR", cast=Path)
    assert result == tmp_path


# ---------------------------------------------------------------------------
# default is returned (not cast) when var is missing
# ---------------------------------------------------------------------------

def test_get_default_bypasses_cast(monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    result = envspec.get("PORT", default=8080, cast=int)
    assert result == 8080


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

def test_get_validate_passes(monkeypatch):
    monkeypatch.setenv("PORT", "8080")
    result = envspec.get("PORT", cast=int, validate=lambda v: 1 <= v <= 65535)
    assert result == 8080


def test_get_validate_fails_raises(monkeypatch):
    monkeypatch.setenv("PORT", "99999")
    with pytest.raises(EnvValidationError, match="failed validation"):
        envspec.get("PORT", cast=int, validate=lambda v: 1 <= v <= 65535)


def test_get_validate_message_contains_name_and_value(monkeypatch):
    monkeypatch.setenv("PORT", "0")
    with pytest.raises(EnvValidationError, match="PORT=0"):
        envspec.get("PORT", cast=int, validate=lambda v: v > 0)


# ---------------------------------------------------------------------------
# reset() is a no-op but must not raise
# ---------------------------------------------------------------------------

def test_reset_does_not_raise():
    envspec.reset()
