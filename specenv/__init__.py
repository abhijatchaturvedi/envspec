"""specenv — zero-dependency typed environment variable loader for Python.

Quick start::

    import specenv

    PORT    = specenv.get("PORT",    default=8080,  cast=int)
    DEBUG   = specenv.get("DEBUG",   default=False, cast=bool)
    TIMEOUT = specenv.get("TIMEOUT", default=30.0,  cast=float)

Schema-based::

    from specenv import Schema, Var

    class Config(Schema):
        PORT   = Var(int,  default=8080)
        DB_URL = Var(str,  required=True)
        DEBUG  = Var(bool, default=False)

    cfg = Config.load()
"""

import os
from typing import Any

from ._caster import cast_value as _cast_value
from ._errors import EnvCastError, EnvValidationError
from ._namespace import Namespace
from ._schema import Schema, Var

__all__ = [
    "get",
    "namespace",
    "reset",
    "Schema",
    "Var",
    "Namespace",
    "EnvCastError",
    "EnvValidationError",
]

__version__ = "0.1.0"

_MISSING: Any = object()


def get(
    name: str,
    *,
    default: Any = _MISSING,
    cast: Any = None,
    validate: Any = None,
) -> Any:
    """Read an environment variable and return it as a typed Python value.

    Parameters
    ----------
    name:
        Name of the environment variable (e.g. ``"PORT"``).
    default:
        Value returned when the variable is not set.  When omitted *and* the
        variable is absent, :py:exc:`EnvCastError` is raised.
    cast:
        Target type.  Supports ``int``, ``float``, ``bool``, ``str``,
        ``list``, ``list[int]``, ``list[float]``, ``list[str]``,
        :py:class:`pathlib.Path`, and any parameterised ``list[T]``.
    validate:
        Callable ``(value) -> bool``.  If it returns ``False`` the cast value
        is rejected with :py:exc:`EnvValidationError`.

    Returns
    -------
    Any
        The (optionally cast and validated) value.

    Raises
    ------
    EnvCastError
        When *name* is unset and no *default* was supplied, or when the raw
        string cannot be converted to *cast*.
    EnvValidationError
        When *validate* returns ``False`` for the cast value.

    Examples
    --------
    >>> import os, specenv
    >>> os.environ["PORT"] = "9000"
    >>> specenv.get("PORT", cast=int)
    9000
    >>> specenv.get("MISSING", default=42)
    42
    """
    raw = os.environ.get(name)

    if raw is None:
        if default is _MISSING:
            raise EnvCastError(
                f"Required variable {name} is not set.\n"
                f"    → Add {name} to your environment or .env file."
            )
        return default

    value = _cast_value(name, raw, cast) if cast is not None else raw

    if validate is not None and not validate(value):
        raise EnvValidationError(
            f"{name}={value!r} failed validation "
            f"(must satisfy the provided lambda)."
        )

    return value


def namespace(prefix: str) -> Namespace:
    """Return a :py:class:`Namespace` that prepends *prefix* to every key.

    Example::

        db = specenv.namespace("DB_")
        host = db.get("HOST", default="localhost")  # reads DB_HOST
        port = db.get("PORT", default=5432, cast=int)  # reads DB_PORT

    Parameters
    ----------
    prefix:
        String prepended to every key passed to :py:meth:`Namespace.get`.
    """
    return Namespace(prefix)


def reset() -> None:
    """Reset internal state.

    A no-op in this release; reserved for future caching layers.  Call it in
    test ``teardown`` fixtures if you want forward-compatibility.
    """
