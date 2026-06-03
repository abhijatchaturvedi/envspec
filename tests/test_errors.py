"""Tests for EnvCastError and EnvValidationError."""

import pytest

from envspec import EnvCastError, EnvValidationError


def test_env_cast_error_is_exception():
    err = EnvCastError("test message")
    assert isinstance(err, Exception)


def test_env_cast_error_message():
    err = EnvCastError("Cannot cast PORT")
    assert "Cannot cast PORT" in str(err)


def test_env_validation_error_is_exception():
    err = EnvValidationError("test message")
    assert isinstance(err, Exception)


def test_env_validation_error_message():
    err = EnvValidationError("PORT=99999 failed validation")
    assert "failed validation" in str(err)


def test_env_cast_error_is_not_validation_error():
    with pytest.raises(EnvCastError):
        raise EnvCastError("oops")


def test_env_validation_error_is_not_cast_error():
    with pytest.raises(EnvValidationError):
        raise EnvValidationError("oops")


def test_errors_are_distinct_types():
    assert EnvCastError is not EnvValidationError


def test_env_cast_error_can_be_caught_as_exception():
    try:
        raise EnvCastError("boom")
    except Exception as exc:
        assert "boom" in str(exc)
    else:
        pytest.fail("Exception not raised")


def test_env_validation_error_can_be_caught_as_exception():
    try:
        raise EnvValidationError("bad value")
    except Exception as exc:
        assert "bad value" in str(exc)
    else:
        pytest.fail("Exception not raised")
