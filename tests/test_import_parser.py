import os
from pathlib import Path

from deptry.import_parser import ImportParser


def test_import_parser_py():
    imported_modules = ImportParser().get_imported_modules_from_file(Path("tests/data/some_imports.py"))
    assert set(imported_modules) == set(["os", "pathlib", "typing", "pandas", "numpy"])


def test_import_parser_ipynb():
    imported_modules = ImportParser().get_imported_modules_from_file(
        Path("tests/data/example_project/src/notebook.ipynb")
    )
    assert set(imported_modules) == set(["click", "urllib3", "toml"])


def test_import_parser_ifelse():
    imported_modules = ImportParser().get_imported_modules_from_str(
        """
x=1
import numpy
if x>0:
    import pandas
elif x<0:
    from typing import List
else:
    import logging
"""
    )
    assert set(imported_modules) == set(["numpy", "pandas", "typing", "logging"])


def test_import_parser_tryexcept():
    imported_modules = ImportParser().get_imported_modules_from_str(
        """
import pandas as pd
from numpy import random
try:
    import click
except:
    import logging
"""
    )
    assert set(imported_modules) == set(["numpy", "pandas", "click", "logging"])


def test_import_parser_func():
    imported_modules = ImportParser().get_imported_modules_from_str(
        """
import pandas as pd
from numpy import random
def func():
    import click
"""
    )
    assert set(imported_modules) == set(["numpy", "pandas", "click"])


def test_import_parser_class():
    imported_modules = ImportParser().get_imported_modules_from_str(
        """
import pandas as pd
from numpy import random
class MyClass:
    def __init__(self):
        import click
"""
    )
    assert set(imported_modules) == set(["numpy", "pandas", "click"])


def test_import_parser_relative():
    imported_modules = ImportParser().get_imported_modules_from_str("""from . import foo\nfrom .foo import bar""")
    assert set(imported_modules) == set([])
