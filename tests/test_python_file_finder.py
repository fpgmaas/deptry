import os
import shlex
import shutil
import subprocess
from contextlib import contextmanager
from pathlib import Path

import pytest

from deptry.python_file_finder import PythonFileFinder


def test_find_only_py_files():
    """
    Should only find src/main.py
    """
    files = PythonFileFinder(ignore_notebooks=True).get_all_python_files_in(
        Path("tests/data/projects/project_with_obsolete")
    )
    assert len(files) == 1
    assert "main.py" in (str(files[0]))


def test_find_py_and_ipynb_files():
    """
    Should find src/main.py and src/notebook.ipynb
    """
    files = PythonFileFinder(ignore_notebooks=False).get_all_python_files_in(
        Path("tests/data/projects/project_with_obsolete")
    )
    assert len(files) == 2
    assert any(["main.py" in str(x) for x in files])
    assert any(["notebook.ipynb" in str(x) for x in files])
