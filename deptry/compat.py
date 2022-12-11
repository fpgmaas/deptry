import sys

if sys.version_info >= (3, 8):
    import importlib.metadata as metadata
    from importlib.metadata import PackageNotFoundError
else:
    import importlib_metadata as metadata
    from importlib_metadata import PackageNotFoundError

__all__ = ("metadata", "PackageNotFoundError")
