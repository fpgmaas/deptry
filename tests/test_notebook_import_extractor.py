import os
from contextlib import contextmanager
from pathlib import Path

import pytest

from deptry.notebook_import_extractor import NotebookImportExtractor


def test_convert_notebook():
    imports = NotebookImportExtractor().extract("tests/data/projects/project_with_obsolete/src/notebook.ipynb")
    assert "import click" in imports[0]
    assert "import requests as req" in imports[1]
    assert len(imports) == 4
