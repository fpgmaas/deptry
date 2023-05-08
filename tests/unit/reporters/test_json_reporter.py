from __future__ import annotations

import json
from pathlib import Path

from deptry.dependency import Dependency
from deptry.imports.location import Location
from deptry.module import Module
from deptry.reporters import JSONReporter
from deptry.violations import (
    MisplacedDevDependencyViolation,
    MissingDependencyViolation,
    TransitiveDependencyViolation,
    UnusedDependencyViolation,
)
from tests.utils import run_within_dir


def test_simple(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        JSONReporter(
            [
                MissingDependencyViolation(Module("foo", package="foo_package"), Location(Path("foo.py"), 1, 2)),
                UnusedDependencyViolation(Dependency("foo", Path("pyproject.toml")), Location(Path("pyproject.toml"))),
                TransitiveDependencyViolation(Module("foo", package="foo_package"), Location(Path("foo/bar.py"), 1, 2)),
                MisplacedDevDependencyViolation(Module("foo", package="foo_package"), Location(Path("foo.py"), 1, 2)),
            ],
            "output.json",
        ).report()

        with open("output.json") as f:
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
                "error": {"code": "DEP003", "message": "'foo_package' imported but it is a transitive dependency"},
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
