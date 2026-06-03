"""Tests for specenv.namespace() / Namespace."""

import pytest

import specenv
from specenv import EnvCastError


def test_namespace_get_string(monkeypatch):
    monkeypatch.setenv("DB_HOST", "localhost")
    db = specenv.namespace("DB_")
    assert db.get("HOST") == "localhost"


def test_namespace_get_int(monkeypatch):
    monkeypatch.setenv("DB_PORT", "5432")
    db = specenv.namespace("DB_")
    assert db.get("PORT", cast=int) == 5432


def test_namespace_get_default(monkeypatch):
    monkeypatch.delenv("DB_HOST", raising=False)
    db = specenv.namespace("DB_")
    assert db.get("HOST", default="localhost") == "localhost"


def test_namespace_get_missing_no_default_raises(monkeypatch):
    monkeypatch.delenv("DB_HOST", raising=False)
    db = specenv.namespace("DB_")
    with pytest.raises(EnvCastError, match="Required variable DB_HOST"):
        db.get("HOST")


def test_namespace_bool(monkeypatch):
    monkeypatch.setenv("APP_DEBUG", "yes")
    app = specenv.namespace("APP_")
    assert app.get("DEBUG", cast=bool) is True


def test_namespace_repr():
    ns = specenv.namespace("MY_")
    assert "MY_" in repr(ns)


def test_namespace_empty_prefix(monkeypatch):
    monkeypatch.setenv("PORT", "9000")
    ns = specenv.namespace("")
    assert ns.get("PORT", cast=int) == 9000


def test_two_namespaces_independent(monkeypatch):
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("CACHE_PORT", "6379")
    db = specenv.namespace("DB_")
    cache = specenv.namespace("CACHE_")
    assert db.get("PORT", cast=int) == 5432
    assert cache.get("PORT", cast=int) == 6379
