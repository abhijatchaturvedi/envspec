"""Namespace (prefix) wrapper for environment variable lookups."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class Namespace:
    """A prefix-scoped view over environment variables.

    All :py:meth:`get` calls prepend *prefix* to the key before lookup.

    Example::

        db = envspec.namespace("DB_")
        host = db.get("HOST", default="localhost")   # reads DB_HOST
        port = db.get("PORT", default=5432, cast=int) # reads DB_PORT
    """

    def __init__(self, prefix: str) -> None:
        """Initialise with *prefix* (e.g. ``"DB_"``)."""
        self._prefix = prefix

    def get(self, key: str, **kwargs: Any) -> Any:
        """Read ``prefix + key`` from the environment.

        Accepts the same keyword arguments as :py:func:`envspec.get`.
        """
        from . import get  # local import avoids circular dependency
        return get(self._prefix + key, **kwargs)

    def __repr__(self) -> str:
        return f"Namespace({self._prefix!r})"
