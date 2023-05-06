from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import TYPE_CHECKING
from unittest import mock

import pytest

from deptry.imports.extract import get_imported_modules_from_file
from tests.utils import run_within_dir

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture


def test_import_parser_py() -> None:
    imported_modules = get_imported_modules_from_file(Path("tests/data/some_imports.py"))

    assert imported_modules == {
        "barfoo",
        "baz",
        "click",
        "foobar",
        "httpx",
        "module_in_class",
        "module_in_func",
        "not_click",
        "numpy",
        "os",
        "pandas",
        "pathlib",
        "randomizer",
        "typing",
    }


def test_import_parser_ipynb() -> None:
    imported_modules = get_imported_modules_from_file(Path("tests/data/example_project/src/notebook.ipynb"))

    assert imported_modules == {"click", "urllib3", "toml"}


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
            "import foo\nmy_string = '🐺'",
            "utf-16",
        ),
    ],
)
def test_import_parser_file_encodings(file_content: str, encoding: str | None, tmp_path: Path) -> None:
    random_file_name = f"file_{uuid.uuid4()}.py"

    with run_within_dir(tmp_path):
        with open(random_file_name, "w", encoding=encoding) as f:
            f.write(file_content)

        assert get_imported_modules_from_file(Path(random_file_name)) == {"foo"}


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

        assert get_imported_modules_from_file(Path(random_file_name)) == {"foo"}


def test_import_parser_file_encodings_warning(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    with run_within_dir(tmp_path):
        with open("file1.py", "w", encoding="utf-8") as f:
            f.write("print('this is a mock unparseable file')")

        with caplog.at_level(logging.WARNING), mock.patch(
            "deptry.imports.extractors.python_import_extractor.ast.parse",
            side_effect=UnicodeDecodeError("fakecodec", b"\x00\x00", 1, 2, "Fake reason!"),
        ):
            assert get_imported_modules_from_file(Path("file1.py")) == set()

        assert "Warning: File file1.py could not be decoded. Skipping..." in caplog.text
