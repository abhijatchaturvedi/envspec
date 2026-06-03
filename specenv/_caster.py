"""Type-casting logic for environment variable values."""

from pathlib import Path
from typing import Any, get_args, get_origin

from ._errors import EnvCastError

_BOOL_TRUE = frozenset({"1", "true", "yes", "on"})
_BOOL_FALSE = frozenset({"0", "false", "no", "off"})


def cast_value(name: str, raw: str, cast_type: Any) -> Any:
    """Cast *raw* (a string from the environment) to *cast_type*.

    Supports: str, int, float, bool, Path, list, list[T].
    Raises EnvCastError with a human-readable message on failure.
    """
    origin = get_origin(cast_type)

    if cast_type is bool:
        lower = raw.lower()
        if lower in _BOOL_TRUE:
            return True
        if lower in _BOOL_FALSE:
            return False
        raise EnvCastError(
            f'Cannot cast {name}={raw!r} to bool.\n'
            f'    → Set {name} to one of: 1/0, true/false, yes/no, on/off'
        )

    if cast_type is int:
        try:
            return int(raw)
        except ValueError:
            raise EnvCastError(
                f'Cannot cast {name}={raw!r} to int.\n'
                f'    → Set {name} to a valid integer (e.g. {name}=8080)'
            ) from None

    if cast_type is float:
        try:
            return float(raw)
        except ValueError:
            raise EnvCastError(
                f'Cannot cast {name}={raw!r} to float.\n'
                f'    → Set {name} to a valid float (e.g. {name}=3.14)'
            ) from None

    if cast_type is str:
        return raw

    if cast_type is Path:
        return Path(raw)

    if cast_type is list:
        if not raw.strip():
            return []
        return [item.strip() for item in raw.split(",")]

    if origin is list:
        args = get_args(cast_type)
        item_type = args[0] if args else str
        if not raw.strip():
            return []
        return [cast_value(name, item.strip(), item_type) for item in raw.split(",")]

    raise EnvCastError(f"Unsupported cast type for {name}: {cast_type!r}")
