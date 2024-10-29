from __future__ import annotations

import json
import logging
import re
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from deptry.imports.extract import get_imported_modules_from_list_of_files
from deptry.imports.location import Location
from tests.utils import run_within_dir

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture


def test_import_parser_py() -> None:
    some_imports_path = Path("tests/fixtures/some_imports.py")

    assert get_imported_modules_from_list_of_files([some_imports_path]) == {
        "barfoo": [Location(some_imports_path, 25, 8)],
        "baz": [Location(some_imports_path, 21, 5)],
        "click": [Location(some_imports_path, 35, 12)],
        "foobar": [Location(some_imports_path, 23, 12)],
        "http": [Location(some_imports_path, line=51, column=1)],
        "httpx": [Location(some_imports_path, 19, 12)],
        "importlib": [
            Location(some_imports_path, line=5, column=1),
            Location(some_imports_path, line=6, column=1),
            Location(some_imports_path, line=7, column=8),
            Location(some_imports_path, line=8, column=8),
        ],
        "module_in_class": [Location(some_imports_path, 46, 16)],
        "module_in_func": [Location(some_imports_path, 41, 12)],
        "not_click": [Location(some_imports_path, 37, 12)],
        "numpy": [
            Location(some_imports_path, 10, 8),
            Location(some_imports_path, 12, 1),
        ],
        "os": [Location(some_imports_path, 2, 1)],
        "pandas": [Location(some_imports_path, 11, 8)],
        "pathlib": [Location(some_imports_path, 3, 1)],
        "patito": [Location(some_imports_path, line=48, column=1)],
        "polars": [Location(some_imports_path, line=49, column=1)],
        "randomizer": [Location(some_imports_path, 26, 1)],
        "typing": [
            Location(some_imports_path, 1, 8),
            Location(some_imports_path, 4, 1),
        ],
        "uvicorn": [Location(some_imports_path, line=50, column=1)],
        "xml": [Location(some_imports_path, line=52, column=1)],
    }


def test_import_parser_ipynb() -> None:
    notebook_path = Path("tests/fixtures/some_imports.ipynb")

    assert get_imported_modules_from_list_of_files([notebook_path]) == {
        "click": [Location(notebook_path, 4, 8)],
        "toml": [Location(notebook_path, 6, 8)],
        "urllib3": [Location(notebook_path, 5, 1)],
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

        assert get_imported_modules_from_list_of_files([random_file]) == {"foo": [Location(random_file, 1, 8)]}


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
            r"WARNING  .*:shared.rs:\d+ Warning: Skipping processing of file_with_bad_encoding.py because of the following error: \"OSError: Failed to decode file content with the detected encoding.\".",
            caplog.text,
        )
        assert re.search(
            r"WARNING  .*:shared.rs:\d+ Warning: Skipping processing of file_with_syntax_error.py because of the following error: \"SyntaxError: Expected an expression at byte range 15..16\".",
            caplog.text,
        )


def test_import_parser_for_ipynb_errors(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    notebook_ok = Path("notebook_ok.ipynb")
    notebook_with_syntax_error = Path("notebook_with_syntax_error.ipynb")

    with run_within_dir(tmp_path):
        # Create a well-formed notebook
        with notebook_ok.open("w") as f:
            json.dump(
                {
                    "cells": [{"cell_type": "code", "source": ["import numpy\n"]}],
                    "metadata": {},
                    "nbformat": 4,
                    "nbformat_minor": 2,
                },
                f,
            )

        # Create a notebook with invalid Python syntax in a code cell
        with notebook_with_syntax_error.open("w") as f:
            json.dump(
                {
                    "cells": [{"cell_type": "code", "source": ["import n invalid_syntax:::\n"]}],
                    "metadata": {},
                    "nbformat": 4,
                    "nbformat_minor": 2,
                },
                f,
            )

        # Execute function and assert the result for well-formed notebook
        with caplog.at_level(logging.WARNING):
            assert get_imported_modules_from_list_of_files([
                notebook_ok,
                notebook_with_syntax_error,
            ]) == {"numpy": [Location(file=Path("notebook_ok.ipynb"), line=1, column=8)]}

        assert re.search(
            r"WARNING  .*:shared.rs:\d+ Warning: Skipping processing of notebook_with_syntax_error.ipynb because of the following error: \"SyntaxError: Expected ',', found name at byte range 9..23\".",
            caplog.text,
        )


def test_python_3_12_f_string_syntax(tmp_path: Path) -> None:
    file_path = Path("file1.py")

    with run_within_dir(tmp_path):
        with file_path.open("w") as f:
            f.write('import foo\nprint(f"abc{"def"}")')

        assert get_imported_modules_from_list_of_files([file_path]) == {"foo": [Location(file_path, 1, 8)]}
