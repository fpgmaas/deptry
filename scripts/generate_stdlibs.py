#!/usr/bin/env python3

# This script is inspired by isort: https://github.com/PyCQA/isort/blob/4ccbd1eddf564d2c9e79c59d59c1fc06a7e35f94/scripts/mkstdlibs.py.

from __future__ import annotations

import ast
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

OUTPUT_PATH = Path("python/deptry/stdlibs.py")
STDLIB_MODULES_URL = "https://docs.python.org/{}.{}/py-modindex.html"

# Starting from Python 3.10, https://docs.python.org/3/library/sys.html#sys.stdlib_module_names is available.
PYTHON_VERSIONS = ((3, 8), (3, 9))

# Modules that are in stdlib, but undocumented.
EXTRA_STDLIBS_MODULES = ("_ast", "ntpath", "posixpath", "sre", "sre_constants", "sre_compile", "sre_parse")

DOCSTRING_GENERATED_FILES = """
DO NOT EDIT THIS FILE MANUALLY.
It is generated from `scripts/generate_stdlibs.py` script and contains the stdlib modules for Python versions that does
not support https://docs.python.org/3/library/sys.html#sys.stdlib_module_names (< 3.10).
The file can be generated again using `python scripts/generate_stdlibs.py`.
"""


class PythonStdlibHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._is_in_code_tag = False
        self.modules: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "code":
            self._is_in_code_tag = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "code":
            self._is_in_code_tag = False

    def handle_data(self, data: str) -> None:
        if self._is_in_code_tag:
            self.modules.append(data)


def get_stdlib_modules_for_python_version(python_version: tuple[int, int]) -> list[str]:
    with urllib.request.urlopen(  # noqa: S310
        STDLIB_MODULES_URL.format(python_version[0], python_version[1])
    ) as response:
        html_content = response.read().decode()

    parser = PythonStdlibHTMLParser()
    parser.feed(html_content)

    modules = {module.split(".")[0] for module in parser.modules}.union(EXTRA_STDLIBS_MODULES)
    modules.remove("__main__")

    return sorted(modules)


def get_stdlib_modules() -> dict[str, list[str]]:
    return {
        f"{python_version[0]}{python_version[1]}": get_stdlib_modules_for_python_version(python_version)
        for python_version in PYTHON_VERSIONS
    }


def write_stdlibs_file(stdlib_python: dict[str, list[str]]) -> None:
    node = ast.Module(
        body=[
            ast.Expr(ast.Constant(DOCSTRING_GENERATED_FILES)),
            ast.Assign(
                targets=[ast.Name("STDLIBS_PYTHON")],
                value=ast.Dict(
                    keys=[ast.Str(python_version) for python_version in stdlib_python],
                    values=[
                        ast.Call(
                            func=ast.Name(id="frozenset"),
                            args=[ast.Set(elts=[ast.Constant(module) for module in python_stdlib_modules])],
                            keywords=[],
                        )
                        for python_stdlib_modules in stdlib_python.values()
                    ],
                ),
                lineno=0,
            ),
        ],
        type_ignores=[],
    )

    with OUTPUT_PATH.open("w+") as stdlib_file:
        stdlib_file.write(ast.unparse(node))  # type: ignore[attr-defined, unused-ignore]


if __name__ == "__main__":
    write_stdlibs_file(get_stdlib_modules())
