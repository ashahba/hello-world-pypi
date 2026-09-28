"""The simplest possible package, used to demonstrate publishing to PyPI."""

from importlib.metadata import PackageNotFoundError, version

try:
    # Single-source the version: it lives in pyproject.toml and is read back
    # from the installed distribution metadata at runtime.
    __version__ = version("hello-world-pypi")
except PackageNotFoundError:  # pragma: no cover - source tree without an install
    __version__ = "0.0.0.dev0"

__all__ = ["__version__", "hello"]


def hello(name: str = "World") -> str:
    """Return a friendly greeting for ``name``."""
    return f"Hello, {name}!"
