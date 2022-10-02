import sys

if sys.version_info >= (3, 8):
    import importlib.metadata as metadata
    from importlib.metadata import PackageNotFoundError
else:
    import importlib_metadata as metadata  # noqa: F401
    from importlib_metadata import PackageNotFoundError  # noqa: F401

__all__ = ("metadata", "PackageNotFoundError")
