from __future__ import annotations

import json
import logging
import re
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from deptry.imports.extract import get_imported_modules_from_ipynb_file, get_imported_modules_from_list_of_files
from deptry.imports.location import Location
from tests.utils import run_within_dir

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture


def test_import_parser_py() -> None:
    some_imports_path = Path("tests/data/some_imports.py")

    assert get_imported_modules_from_list_of_files([some_imports_path]) == {
        "barfoo": [Location(some_imports_path, 20, 8)],
        "baz": [Location(some_imports_path, 16, 5)],
        "click": [Location(some_imports_path, 24, 12)],
        "foobar": [Location(some_imports_path, 18, 12)],
        "httpx": [Location(some_imports_path, 14, 12)],
        "module_in_class": [Location(some_imports_path, 35, 16)],
        "module_in_func": [Location(some_imports_path, 30, 12)],
        "not_click": [Location(some_imports_path, 26, 12)],
        "numpy": [
            Location(some_imports_path, 5, 8),
            Location(some_imports_path, 7, 1),
        ],
        "os": [Location(some_imports_path, 1, 1)],
        "pandas": [Location(some_imports_path, 6, 8)],
        "pathlib": [Location(some_imports_path, 2, 1)],
        "randomizer": [Location(some_imports_path, 21, 1)],
        "typing": [Location(some_imports_path, 3, 1)],
    }


def test_import_parser_ipynb() -> None:
    notebook_path = Path("tests/data/example_project/src/notebook.ipynb")

    assert get_imported_modules_from_ipynb_file(notebook_path) == {
        "click": [Location(notebook_path, 1, 0)],
        "toml": [Location(notebook_path, 5, 0)],
        "urllib3": [Location(notebook_path, 3, 0)],
    }


@pytest.mark.parametrize(
    ("file_content", "encoding"),
    [
        (
            "# -*- encoding: utf-8 -*-\nimport foo\nprint('嘉大')",
            "utf-8",
        ),
        (
            "# -*- encoding: iso-8859-15 -*-\nimport foo\nprint('Æ	Ç')",
            "iso-8859-15",
        ),
        (
            "# -*- encoding: utf-16 -*-\nimport foo\nprint('嘉大')",
            "utf-16",
        ),
        (
            "\nimport foo\nmy_string = '🐺'",
            "utf-16",
        ),
    ],
)
def test_import_parser_file_encodings(file_content: str, encoding: str | None, tmp_path: Path) -> None:
    random_file = Path(f"file_{uuid.uuid4()}.py")

    with run_within_dir(tmp_path):
        with random_file.open("w", encoding=encoding) as f:
            f.write(file_content)

        assert get_imported_modules_from_list_of_files([random_file]) == {"foo": [Location(random_file, 2, 8)]}


@pytest.mark.parametrize(
    ("code_cell_content", "encoding"),
    [
        (
            ["import foo", "print('嘉大')"],
            "utf-8",
        ),
        (
            ["import foo", "print('Æ	Ç')"],
            "iso-8859-15",
        ),
        (
            ["import foo", "print('嘉大')"],
            "utf-16",
        ),
        (
            ["import foo", "my_string = '🐺'"],
            None,
        ),
    ],
)
def test_import_parser_file_encodings_ipynb(code_cell_content: list[str], encoding: str | None, tmp_path: Path) -> None:
    random_file = Path(f"file_{uuid.uuid4()}.ipynb")

    with run_within_dir(tmp_path):
        with random_file.open("w", encoding=encoding) as f:
            file_content = {
                "cells": [
                    {
                        "cell_type": "code",
                        "metadata": {},
                        "source": code_cell_content,
                    }
                ]
            }
            f.write(json.dumps(file_content))

        assert get_imported_modules_from_list_of_files([random_file]) == {"foo": [Location(random_file, 1, 0)]}


def test_import_parser_errors(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    file_ok = Path("file_ok.py")
    file_with_bad_encoding = Path("file_with_bad_encoding.py")
    file_with_syntax_error = Path("file_with_syntax_error.py")

    with run_within_dir(tmp_path):
        with file_ok.open("w") as f:
            f.write("import black")

        with file_with_bad_encoding.open("w", encoding="ISO-8859-1") as f:
            f.write("# -*- coding: utf-8 -*-\nprint('ÆØÅ')")

        with file_with_syntax_error.open("w") as f:
            f.write("invalid_syntax:::")

        with caplog.at_level(logging.WARNING):
            assert get_imported_modules_from_list_of_files([
                file_ok,
                file_with_bad_encoding,
                file_with_syntax_error,
            ]) == {"black": [Location(file=Path("file_ok.py"), line=1, column=8)]}

        assert re.search(
            r"WARNING  deptry.imports:imports.rs:\d+ Warning: Skipping processing of file_with_bad_encoding.py because of the following error: \"OSError: Failed to decode file content with the detected encoding.\".",
            caplog.text,
        )
        assert re.search(
            r"WARNING  deptry.imports:imports.rs:\d+ Warning: Skipping processing of file_with_syntax_error.py because of the following error: \"SyntaxError: invalid syntax. Got unexpected token ':' at byte offset 15\".",
            caplog.text,
        )
