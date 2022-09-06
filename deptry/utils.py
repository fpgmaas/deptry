import os
import sys
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def run_within_dir(path: Path):
    """
    Utility function to run some code within a directory, and change back to the current directory afterwards.

    Example usage:

    ```
    with run_within_dir(directory):
        some_code()
    ```

    """
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def import_importlib_metadata():
    """
    importlib.metadata is in the standard library since Python version 3.8
    """
    if sys.version_info[1] == 7:
        import importlib_metadata as metadata
        from importlib_metadata import PackageNotFoundError

        return metadata, PackageNotFoundError
    else:
        import importlib.metadata as metadata
        from importlib.metadata import PackageNotFoundError

        return metadata, PackageNotFoundError
