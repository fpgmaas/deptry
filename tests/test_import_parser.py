import os
from pathlib import Path

from deptry.import_parser import ImportParser


def test_import_parser_py():
    imported_modules = ImportParser()._get_imported_modules_from_file(Path("tests/data/some_imports.py"))
    assert set(imported_modules) == set(["os", "pathlib", "typing", "pandas", "numpy"])


def test_import_parser_ipynb():
    imported_modules = ImportParser()._get_imported_modules_from_file(
        Path("tests/data/projects/project_with_obsolete/src/notebook.ipynb")
    )
    assert set(imported_modules) == set(["click", "pandas", "numpy", "cookiecutter_poetry"])
