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
    assert get_imported_modules_from_file(Path("tests/data/some_imports.py")) == {
        "barfoo": [Location(Path("tests/data/some_imports.py"), 20, 0)],
        "baz": [Location(Path("tests/data/some_imports.py"), 16, 4)],
        "click": [Location(Path("tests/data/some_imports.py"), 24, 4)],
        "foobar": [Location(Path("tests/data/some_imports.py"), 18, 4)],
        "httpx": [Location(Path("tests/data/some_imports.py"), 14, 4)],
        "module_in_class": [Location(Path("tests/data/some_imports.py"), 35, 8)],
        "module_in_func": [Location(Path("tests/data/some_imports.py"), 30, 4)],
        "not_click": [Location(Path("tests/data/some_imports.py"), 26, 4)],
        "numpy": [
            Location(Path("tests/data/some_imports.py"), 5, 0),
            Location(Path("tests/data/some_imports.py"), 7, 0),
        ],
        "os": [Location(Path("tests/data/some_imports.py"), 1, 0)],
        "pandas": [Location(Path("tests/data/some_imports.py"), 6, 0)],
        "pathlib": [Location(Path("tests/data/some_imports.py"), 2, 0)],
        "randomizer": [Location(Path("tests/data/some_imports.py"), 21, 0)],
        "typing": [Location(Path("tests/data/some_imports.py"), 3, 0)],
    }


def test_import_parser_ipynb() -> None:
    assert get_imported_modules_from_file(Path("tests/data/example_project/src/notebook.ipynb")) == {
        "click": [Location(Path("tests/data/example_project/src/notebook.ipynb"), 1, 0)],
        "toml": [Location(Path("tests/data/example_project/src/notebook.ipynb"), 5, 0)],
        "urllib3": [Location(Path("tests/data/example_project/src/notebook.ipynb"), 3, 0)],
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
    random_file_name = f"file_{uuid.uuid4()}.py"

    with run_within_dir(tmp_path):
        with open(random_file_name, "w", encoding=encoding) as f:
            f.write(file_content)

        assert get_imported_modules_from_file(Path(random_file_name)) == {
            "foo": [Location(Path(f"{random_file_name}"), 2, 0)]
        }


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
    random_file_name = f"file_{uuid.uuid4()}.ipynb"

    with run_within_dir(tmp_path):
        with open(random_file_name, "w", encoding=encoding) as f:
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

        assert get_imported_modules_from_file(Path(random_file_name)) == {
            "foo": [Location(Path(f"{random_file_name}"), 1, 0)]
        }


def test_import_parser_file_encodings_warning(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    with run_within_dir(tmp_path):
        with open("file1.py", "w", encoding="utf-8") as f:
            f.write("print('this is a mock unparseable file')")

        with caplog.at_level(logging.WARNING), mock.patch(
            "deptry.imports.extractors.python_import_extractor.ast.parse",
            side_effect=UnicodeDecodeError("fakecodec", b"\x00\x00", 1, 2, "Fake reason!"),
        ):
            assert get_imported_modules_from_file(Path("file1.py")) == {}

        assert "Warning: File file1.py could not be decoded. Skipping..." in caplog.text
