import os
from contextlib import contextmanager
from pathlib import Path

import pytest

from deptry.notebook_converter import NotebookConverter


def test_convert_notebook(tmp_path):
    py_file_path = NotebookConverter(str(tmp_path)).convert(
        "tests/data/projects/project_with_obsolete/src/notebook.ipynb", output_file_name="test"
    )
    assert os.listdir(tmp_path)[0] == "test.py"
