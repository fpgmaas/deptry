from __future__ import annotations

from pathlib import Path

from deptry.imports.location import Location
from deptry.module import Module
from deptry.violations import DEP001MissingDependencyViolation, DEP004MisplacedDevDependencyViolation
from deptry.violations.finder import _get_sorted_violations


def test__get_sorted_violations() -> None:
    violations = [
        DEP004MisplacedDevDependencyViolation(Module("foo"), Location(Path("foo.py"), 1, 0)),
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("foo.py"), 2, 0)),
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("foo.py"), 1, 0)),
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("bar.py"), 3, 1)),
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("bar.py"), 2, 1)),
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("bar.py"), 3, 0)),
    ]

    assert _get_sorted_violations(violations) == [
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("bar.py"), 2, 1)),
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("bar.py"), 3, 0)),
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("bar.py"), 3, 1)),
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("foo.py"), 1, 0)),
        DEP004MisplacedDevDependencyViolation(Module("foo"), Location(Path("foo.py"), 1, 0)),
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("foo.py"), 2, 0)),
    ]
