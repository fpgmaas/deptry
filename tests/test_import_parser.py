import os
from pathlib import Path

from deptry.import_parser import ImportParser


def test_import_parser():
    imported_modules = ImportParser().get_imported_modules_for_file(Path("tests/data/some_imports.py"))
    assert set(imported_modules) == set(["os", "pathlib", "typing", "pandas", "numpy"])
