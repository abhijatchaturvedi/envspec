"""Tests for Schema and Var."""

import pytest

from specenv import EnvCastError, EnvValidationError, Schema, Var


class AppConfig(Schema):
    PORT = Var(int, default=8080)
    DEBUG = Var(bool, default=False)
    DB_URL = Var(str, required=True)
    TIMEOUT = Var(float, default=30.0)
    ALLOWED_IPS = Var(list[str], default=[])


# ---------------------------------------------------------------------------
# Happy-path loading
# ---------------------------------------------------------------------------

def test_schema_load_defaults(monkeypatch):
    monkeypatch.setenv("DB_URL", "postgresql://localhost/db")
    config = AppConfig.load()
    assert config.PORT == 8080
    assert config.DEBUG is False
    assert config.TIMEOUT == 30.0
    assert config.ALLOWED_IPS == []


def test_schema_load_overrides_defaults(monkeypatch):
    monkeypatch.setenv("DB_URL", "sqlite:///test.db")
    monkeypatch.setenv("PORT", "5432")
    monkeypatch.setenv("DEBUG", "true")
    config = AppConfig.load()
    assert config.PORT == 5432
    assert config.DEBUG is True
    assert config.DB_URL == "sqlite:///test.db"


def test_schema_load_list_field(monkeypatch):
    monkeypatch.setenv("DB_URL", "x")
    monkeypatch.setenv("ALLOWED_IPS", "192.168.1.1,10.0.0.1")
    config = AppConfig.load()
    assert config.ALLOWED_IPS == ["192.168.1.1", "10.0.0.1"]


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

def test_schema_required_missing_raises(monkeypatch):
    monkeypatch.delenv("DB_URL", raising=False)
    with pytest.raises(EnvCastError, match="DB_URL"):
        AppConfig.load()


def test_schema_cast_error_propagates(monkeypatch):
    monkeypatch.setenv("DB_URL", "x")
    monkeypatch.setenv("PORT", "not-a-number")
    with pytest.raises(EnvCastError, match="PORT"):
        AppConfig.load()


def test_schema_multiple_errors_combined(monkeypatch):
    monkeypatch.delenv("DB_URL", raising=False)
    monkeypatch.setenv("PORT", "bad")
    with pytest.raises(EnvCastError, match="Multiple configuration errors"):
        AppConfig.load()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_schema_validate(monkeypatch):
    class Cfg(Schema):
        PORT = Var(int, default=8080, validate=lambda v: 1 <= v <= 65535)

    monkeypatch.setenv("PORT", "99999")
    with pytest.raises(EnvValidationError, match="failed validation"):
        Cfg.load()


# ---------------------------------------------------------------------------
# Custom env dict (useful for testing without touching os.environ)
# ---------------------------------------------------------------------------

def test_schema_load_custom_env():
    config = AppConfig.load(env={"DB_URL": "redis://localhost", "PORT": "6379"})
    assert config.PORT == 6379
    assert config.DB_URL == "redis://localhost"


# ---------------------------------------------------------------------------
# Inheritance
# ---------------------------------------------------------------------------

def test_schema_inheritance(monkeypatch):
    class Base(Schema):
        PORT = Var(int, default=8080)

    class Child(Base):
        DEBUG = Var(bool, default=False)

    config = Child.load(env={})
    assert config.PORT == 8080
    assert config.DEBUG is False


# ---------------------------------------------------------------------------
# Var descriptor behaviour
# ---------------------------------------------------------------------------

def test_var_class_access_returns_descriptor():
    assert isinstance(AppConfig.__dict__["PORT"], Var)


def test_var_required_and_default_raises():
    with pytest.raises(ValueError, match="required=True"):
        Var(str, required=True, default="oops")
