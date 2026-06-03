"""Schema base class and Var descriptor for declarative environment config."""

from __future__ import annotations

from typing import Any, Callable

from ._errors import EnvCastError, EnvValidationError

_MISSING: Any = object()


class Var:
    """Descriptor that declares a single typed environment variable.

    Parameters
    ----------
    cast_type:
        The target Python type (e.g. ``int``, ``bool``, ``list[str]``).
    default:
        Value to use when the variable is absent. Mutually exclusive with
        *required*.
    required:
        When ``True`` and the variable is absent, :py:meth:`Schema.load`
        raises :py:exc:`EnvCastError`.
    validate:
        Optional callable ``(value) -> bool``.  If it returns ``False`` for
        the cast value, :py:exc:`EnvValidationError` is raised.

    Example::

        class Config(Schema):
            PORT = Var(int, default=8080)
            DB_URL = Var(str, required=True)
    """

    def __init__(
        self,
        cast_type: Any,
        *,
        default: Any = _MISSING,
        required: bool = False,
        validate: Callable[[Any], bool] | None = None,
    ) -> None:
        if required and default is not _MISSING:
            raise ValueError("Var cannot have both required=True and a default value.")
        self.cast_type = cast_type
        self.default = default
        self.required = required
        self.validate = validate
        self.name: str = ""  # set by __set_name__

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        try:
            return obj.__dict__[self.name]
        except KeyError:
            if self.default is not _MISSING:
                return self.default
            raise AttributeError(self.name) from None

    def __set__(self, obj: Any, value: Any) -> None:
        obj.__dict__[self.name] = value


class Schema:
    """Base class for declarative, type-safe environment variable schemas.

    Subclass :py:class:`Schema` and declare attributes as :py:class:`Var`
    instances, then call :py:meth:`load` to populate them from the environment.

    Example::

        class AppConfig(Schema):
            PORT    = Var(int, default=8080)
            DB_URL  = Var(str, required=True)
            DEBUG   = Var(bool, default=False)

        config = AppConfig.load()
        print(config.PORT)
    """

    @classmethod
    def load(cls, env: dict[str, str] | None = None) -> "Schema":
        """Read all declared :py:class:`Var` fields from the environment.

        Parameters
        ----------
        env:
            Mapping to read from (defaults to :py:data:`os.environ`).  Pass a
            plain ``dict`` in tests to avoid touching the real environment.

        Raises
        ------
        EnvCastError
            When a required variable is missing or a value cannot be cast.
        EnvValidationError
            When a value fails its *validate* callable.
        """
        import os as _os
        from ._caster import cast_value

        if env is None:
            env = dict(_os.environ)

        instance = cls.__new__(cls)
        errors: list[Exception] = []

        # Walk MRO so that inherited Var fields are included.
        seen: set[str] = set()
        for klass in cls.__mro__:
            for attr_name, val in vars(klass).items():
                if attr_name in seen or not isinstance(val, Var):
                    continue
                seen.add(attr_name)
                var: Var = val
                name = var.name or attr_name
                raw = env.get(name)

                if raw is None:
                    if var.required or var.default is _MISSING:
                        errors.append(
                            EnvCastError(
                                f"Required variable {name} is not set.\n"
                                f"    → Add {name} to your environment or .env file."
                            )
                        )
                    else:
                        instance.__dict__[attr_name] = var.default
                    continue

                try:
                    value = cast_value(name, raw, var.cast_type)
                except EnvCastError as exc:
                    errors.append(exc)
                    continue

                if var.validate is not None and not var.validate(value):
                    errors.append(
                        EnvValidationError(
                            f"{name}={value!r} failed validation "
                            f"(must satisfy the provided lambda)."
                        )
                    )
                    continue

                instance.__dict__[attr_name] = value

        if errors:
            if len(errors) == 1:
                raise errors[0]
            combined = "\n".join(str(e) for e in errors)
            raise EnvCastError(f"Multiple configuration errors:\n{combined}")

        return instance
