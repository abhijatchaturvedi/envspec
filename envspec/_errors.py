"""Custom exceptions for envspec."""


class EnvCastError(Exception):
    """Raised when an environment variable cannot be cast to the requested type,
    or when a required variable is missing."""


class EnvValidationError(Exception):
    """Raised when a cast value fails a user-supplied validate callable."""
