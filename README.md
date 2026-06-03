# specenv

**Zero-dependency typed environment variable loader for Python**

[![PyPI version](https://img.shields.io/pypi/v/specenv)](https://pypi.org/project/specenv/)
[![Python versions](https://img.shields.io/pypi/pyversions/specenv)](https://pypi.org/project/specenv/)
[![License MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/abhijatchaturvedi/specenv/actions/workflows/ci.yml/badge.svg)](https://github.com/abhijatchaturvedi/specenv/actions/workflows/ci.yml)

---

## The Problem

Reading environment variables in plain Python is verbose, fragile, and
produces cryptic errors at runtime:

```python
import os

PORT    = int(os.environ.get("PORT", "8080"))
DEBUG   = os.environ.get("DEBUG", "false").lower() in ("1", "true", "yes")
TIMEOUT = float(os.environ.get("TIMEOUT", "30.0"))
HOSTS   = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()]

# If PORT is "abc" you get:
# ValueError: invalid literal for int() with base 10: 'abc'
# — no variable name, no hint on how to fix it.
```

## The Solution

```python
import specenv

PORT    = specenv.get("PORT",           default=8080,  cast=int)
DEBUG   = specenv.get("DEBUG",          default=False, cast=bool)
TIMEOUT = specenv.get("TIMEOUT",        default=30.0,  cast=float)
HOSTS   = specenv.get("ALLOWED_HOSTS",  default=[],    cast=list)

# If PORT is "abc" you get:
# EnvCastError: Cannot cast PORT="abc" to int.
#     → Set PORT to a valid integer (e.g. PORT=8080)
```

---

## Install

```bash
pip install specenv
```

Python 3.10+ required. No runtime dependencies.

---

## Usage

### Simple `get`

```python
import specenv

PORT    = specenv.get("PORT",    default=8080,  cast=int)
DEBUG   = specenv.get("DEBUG",   default=False, cast=bool)
TIMEOUT = specenv.get("TIMEOUT", default=30.0,  cast=float)
HOSTS   = specenv.get("ALLOWED_HOSTS", default=[], cast=list)        # list[str]
PORTS   = specenv.get("PORTS",   default=[8080],  cast=list[int])    # list[int]
```

When `default` is omitted and the variable is not set, `EnvCastError` is
raised immediately.

### Bool casting

| Environment value | Result  |
|-------------------|---------|
| `1`, `true`, `yes`, `on`  | `True`  |
| `0`, `false`, `no`, `off` | `False` |
| anything else             | `EnvCastError` |

Matching is **case-insensitive** (`TRUE`, `Yes`, `ON` all work).

### Schema-based loading

Group all variables into a single class for easier testing and injection:

```python
from specenv import Schema, Var

class AppConfig(Schema):
    PORT        = Var(int,      default=8080)
    DEBUG       = Var(bool,     default=False)
    DB_URL      = Var(str,      required=True)
    TIMEOUT     = Var(float,    default=30.0)
    ALLOWED_IPS = Var(list[str], default=[])

config = AppConfig.load()
print(config.PORT)   # 8080 (or whatever PORT is set to)
```

Pass a plain `dict` to `load()` in tests to avoid touching the real environment:

```python
cfg = AppConfig.load(env={"DB_URL": "sqlite:///test.db"})
```

### Validation

```python
PORT = specenv.get(
    "PORT",
    cast=int,
    validate=lambda v: 1 <= v <= 65535,
)
```

Or inside a Schema:

```python
class Config(Schema):
    PORT = Var(int, default=8080, validate=lambda v: 1 <= v <= 65535)
```

### Namespace / prefix

```python
db    = specenv.namespace("DB_")
HOST  = db.get("HOST", default="localhost")      # reads DB_HOST
PORT  = db.get("PORT", default=5432, cast=int)   # reads DB_PORT

cache = specenv.namespace("CACHE_")
URL   = cache.get("URL", default="redis://localhost:6379")  # reads CACHE_URL
```

---

## Error Messages

Every error is designed to tell you **what went wrong** and **how to fix it**.

```
EnvCastError: Cannot cast PORT="abc" to int.
    → Set PORT to a valid integer (e.g. PORT=8080)

EnvCastError: Required variable DB_URL is not set.
    → Add DB_URL to your environment or .env file.

EnvValidationError: PORT=99999 failed validation (must satisfy the provided lambda).
```

---

## API Reference

| Symbol | Description |
|--------|-------------|
| `specenv.get(name, *, default, cast, validate)` | Read and optionally cast one variable |
| `specenv.namespace(prefix)` | Return a `Namespace` that prepends `prefix` to every key |
| `specenv.reset()` | Reset internal state (no-op in 0.1.0; safe to call in teardowns) |
| `Schema` | Base class for declarative config |
| `Var(cast_type, *, default, required, validate)` | Field descriptor used inside a `Schema` |
| `Namespace` | Prefix-scoped view returned by `namespace()` |
| `EnvCastError` | Raised on missing required variable or bad cast |
| `EnvValidationError` | Raised when a validate callable returns `False` |

**Supported `cast` types:** `int`, `float`, `bool`, `str`, `list`,
`list[int]`, `list[float]`, `list[str]`, `pathlib.Path`, and any
`list[T]` where `T` is one of the above.

---

## Contributing

Bug reports and pull requests are welcome on the
[GitHub issues page](https://github.com/abhijatchaturvedi/specenv/issues).
Please open an issue before starting large changes so we can discuss the
approach first.

---

## License

MIT — see [LICENSE](LICENSE).
