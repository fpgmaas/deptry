from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import TYPE_CHECKING
from unittest import mock

import pytest

from deptry.imports.extract import get_imported_modules_from_file
from deptry.imports.location import Location
from tests.utils import run_within_dir

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture


def test_import_parser_py() -> None:
    some_imports_path = Path("tests/data/some_imports.py")

    assert get_imported_modules_from_file(some_imports_path) == {
        "barfoo": [Location(some_imports_path, 20, 0)],
        "baz": [Location(some_imports_path, 16, 4)],
        "click": [Location(some_imports_path, 24, 4)],
        "foobar": [Location(some_imports_path, 18, 4)],
        "httpx": [Location(some_imports_path, 14, 4)],
        "module_in_class": [Location(some_imports_path, 35, 8)],
        "module_in_func": [Location(some_imports_path, 30, 4)],
        "not_click": [Location(some_imports_path, 26, 4)],
        "numpy": [
            Location(some_imports_path, 5, 0),
            Location(some_imports_path, 7, 0),
        ],
        "os": [Location(some_imports_path, 1, 0)],
        "pandas": [Location(some_imports_path, 6, 0)],
        "pathlib": [Location(some_imports_path, 2, 0)],
        "randomizer": [Location(some_imports_path, 21, 0)],
        "typing": [Location(some_imports_path, 3, 0)],
    }


def test_import_parser_ipynb() -> None:
    notebook_path = Path("tests/data/example_project/src/notebook.ipynb")

    assert get_imported_modules_from_file(notebook_path) == {
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

        assert get_imported_modules_from_file(random_file) == {"foo": [Location(random_file, 2, 0)]}


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

        assert get_imported_modules_from_file(random_file) == {"foo": [Location(random_file, 1, 0)]}


def test_import_parser_file_encodings_warning(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    file_path = Path("file1.py")

    with run_within_dir(tmp_path):
        with file_path.open("w", encoding="utf-8") as f:
            f.write("print('this is a mock unparseable file')")

        with caplog.at_level(logging.WARNING), mock.patch(
            "deptry.imports.extractors.python_import_extractor.ast.parse",
            side_effect=UnicodeDecodeError("fakecodec", b"\x00\x00", 1, 2, "Fake reason!"),
        ):
            assert get_imported_modules_from_file(file_path) == {}

        assert "Warning: File file1.py could not be decoded. Skipping..." in caplog.text
