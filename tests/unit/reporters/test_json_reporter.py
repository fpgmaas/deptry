from __future__ import annotations

import json
from pathlib import Path

from deptry.dependency import Dependency
from deptry.issues_finder.misplaced_dev import MisplacedDevDependenciesFinder
from deptry.issues_finder.missing import MissingDependenciesFinder
from deptry.issues_finder.obsolete import ObsoleteDependenciesFinder
from deptry.issues_finder.transitive import TransitiveDependenciesFinder
from deptry.module import Module
from deptry.reporters import JSONReporter
from deptry.violation import Violation
from tests.utils import run_within_dir


def test_simple(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        JSONReporter(
            {
                "missing": [Violation(MissingDependenciesFinder, Module("foo", package="foo_package"))],
                "obsolete": [Violation(ObsoleteDependenciesFinder, Dependency("foo", Path("pyproject.toml")))],
                "transitive": [Violation(TransitiveDependenciesFinder, Module("foo", package="foo_package"))],
                "misplaced_dev": [Violation(MisplacedDevDependenciesFinder, Module("foo", package="foo_package"))],
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
