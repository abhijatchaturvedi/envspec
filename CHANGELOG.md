# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-03

### Added
- `envspec.get()` with `cast`, `default`, and `validate` parameters
- `Schema` and `Var` for declarative, class-based configuration
- `Namespace` prefix wrapper via `envspec.namespace()`
- `EnvCastError` and `EnvValidationError` with human-readable messages
- Support for `int`, `float`, `bool`, `str`, `list`, `list[T]`, `pathlib.Path`
- Bool casting: `1/0`, `true/false`, `yes/no`, `on/off` (case-insensitive)
- CI workflow: pytest across Python 3.10, 3.11, 3.12, 3.13
- Publish workflow: upload to PyPI on GitHub Release
