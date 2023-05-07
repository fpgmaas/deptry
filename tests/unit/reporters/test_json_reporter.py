from __future__ import annotations

import json
from pathlib import Path

from deptry.dependency import Dependency
from deptry.module import Module
from deptry.reporters import JSONReporter
from deptry.violations import (
    MisplacedDevDependencyViolation,
    MissingDependencyViolation,
    ObsoleteDependencyViolation,
    TransitiveDependencyViolation,
)
from tests.utils import run_within_dir


def test_simple(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        JSONReporter(
            {
                "missing": [MissingDependencyViolation(Module("foo", package="foo_package"))],
                "obsolete": [ObsoleteDependencyViolation(Dependency("foo", Path("pyproject.toml")))],
                "transitive": [TransitiveDependencyViolation(Module("foo", package="foo_package"))],
                "misplaced_dev": [MisplacedDevDependencyViolation(Module("foo", package="foo_package"))],
            },
            "output.json",
        ).report()

        with open("output.json") as f:
            data = json.load(f)

        assert data == {
            "missing": ["foo"],
            "obsolete": ["foo"],
            "transitive": ["foo_package"],
            "misplaced_dev": ["foo"],
        }
