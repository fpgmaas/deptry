from email.generator import Generator
import os
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def run_within_dir(path: Path) -> Generator:
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
