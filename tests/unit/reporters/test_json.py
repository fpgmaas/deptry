from __future__ import annotations

import json
from pathlib import Path

from deptry.dependency import Dependency
from deptry.imports.location import Location
from deptry.module import Module
from deptry.reporters import JSONReporter
from deptry.violations import (
    DEP001MissingDependencyViolation,
    DEP002UnusedDependencyViolation,
    DEP003TransitiveDependencyViolation,
    DEP004MisplacedDevDependencyViolation,
)
from tests.utils import run_within_dir


def test_simple(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        JSONReporter(
            [
                DEP001MissingDependencyViolation(Module("foo", package="foo-package"), Location(Path("foo.py"), 1, 2)),
                DEP002UnusedDependencyViolation(
                    Dependency("foo", Path("pyproject.toml")), Location(Path("pyproject.toml"))
                ),
                DEP003TransitiveDependencyViolation(
                    Module("foo", package="foo-package"), Location(Path("foo/bar.py"), 1, 2)
                ),
                DEP004MisplacedDevDependencyViolation(
                    Module("foo", package="foo-package"), Location(Path("foo.py"), 1, 2)
                ),
            ],
            "output.json",
        ).report()

        with Path("output.json").open() as f:
            data = json.load(f)

        assert data == [
            {
                "error": {"code": "DEP001", "message": "'foo' imported but missing from the dependency definitions"},
                "module": "foo",
                "location": {
                    "file": str(Path("foo.py")),
                    "line": 1,
                    "column": 2,
                },
            },
            {
                "error": {"code": "DEP002", "message": "'foo' defined as a dependency but not used in the codebase"},
                "module": "foo",
                "location": {
                    "file": str(Path("pyproject.toml")),
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {"code": "DEP003", "message": "'foo' imported but it is a transitive dependency"},
                "module": "foo",
                "location": {
                    "file": str(Path("foo/bar.py")),
                    "line": 1,
                    "column": 2,
                },
            },
            {
                "error": {"code": "DEP004", "message": "'foo' imported but declared as a dev dependency"},
                "module": "foo",
                "location": {
                    "file": str(Path("foo.py")),
                    "line": 1,
                    "column": 2,
                },
            },
        ]
