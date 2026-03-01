from __future__ import annotations

from pathlib import Path

from deptry.imports.location import Location
from deptry.module import Module
from deptry.violations import DEP001MissingDependencyViolation, DEP004MisplacedDevDependencyViolation
from deptry.violations.finder import _filter_inline_ignored_violations, _get_sorted_violations


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


def test__filter_inline_ignored_violations_no_ignored_codes() -> None:
    violations = [
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("foo.py"), 1, 0)),
        DEP001MissingDependencyViolation(Module("bar"), Location(Path("bar.py"), 2, 0)),
    ]

    assert _filter_inline_ignored_violations(violations) == violations


def test__filter_inline_ignored_violations_with_matching_code() -> None:
    violations = [
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("foo.py"), 1, 0, ignored_rule_codes=("DEP001",))),
        DEP001MissingDependencyViolation(Module("bar"), Location(Path("bar.py"), 2, 0)),
    ]

    assert _filter_inline_ignored_violations(violations) == [
        DEP001MissingDependencyViolation(Module("bar"), Location(Path("bar.py"), 2, 0)),
    ]


def test__filter_inline_ignored_violations_with_non_matching_code() -> None:
    violations = [
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("foo.py"), 1, 0, ignored_rule_codes=("DEP004",))),
    ]

    assert _filter_inline_ignored_violations(violations) == violations


def test__filter_inline_ignored_violations_with_bare_ignore() -> None:
    violations = [
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("foo.py"), 1, 0, ignored_rule_codes=("ALL",))),
        DEP004MisplacedDevDependencyViolation(
            Module("bar"), Location(Path("bar.py"), 2, 0, ignored_rule_codes=("ALL",))
        ),
    ]

    assert _filter_inline_ignored_violations(violations) == []


def test__filter_inline_ignored_violations_with_multiple_codes() -> None:
    violations = [
        DEP001MissingDependencyViolation(
            Module("foo"), Location(Path("foo.py"), 1, 0, ignored_rule_codes=("DEP001", "DEP004"))
        ),
        DEP004MisplacedDevDependencyViolation(
            Module("bar"), Location(Path("bar.py"), 2, 0, ignored_rule_codes=("DEP001", "DEP004"))
        ),
    ]

    assert _filter_inline_ignored_violations(violations) == []
