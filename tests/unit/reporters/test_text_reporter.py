from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from deptry.dependency import Dependency
from deptry.imports.location import Location
from deptry.module import Module
from deptry.reporters import TextReporter
from deptry.violations import (
    MisplacedDevDependencyViolation,
    MissingDependencyViolation,
    ObsoleteDependencyViolation,
    TransitiveDependencyViolation,
)

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture


def test_logging_number_multiple(caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        violations = [
            MissingDependencyViolation(Module("foo", package="foo_package"), Location(Path("foo.py"), 1, 2)),
            ObsoleteDependencyViolation(Dependency("foo", Path("pyproject.toml")), Location(Path("pyproject.toml"))),
            TransitiveDependencyViolation(Module("foo", package="foo_package"), Location(Path("foo/bar.py"), 1, 2)),
            MisplacedDevDependencyViolation(Module("foo", package="foo_package"), Location(Path("foo.py"), 1, 2)),
        ]
        TextReporter(violations).report()

    assert caplog.messages == [
        "",
        f"{str(Path('foo.py'))}:1:2: DEP001 foo imported but missing from the dependency definitions",
        f"{str(Path('pyproject.toml'))}: DEP002 foo defined as a dependency but not used in the codebase",
        f"{str(Path('foo/bar.py'))}:1:2: DEP003 foo_package imported but it is a transitive dependency",
        f"{str(Path('foo.py'))}:1:2: DEP004 foo imported but declared as a dev dependency",
        "Found 4 dependency issues.",
        "\nFor more information, see the documentation: https://fpgmaas.github.io/deptry/",
    ]


def test_logging_number_single(caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        TextReporter(
            [MissingDependencyViolation(Module("foo", package="foo_package"), Location(Path("foo.py"), 1, 2))]
        ).report()

    assert caplog.messages == [
        "",
        "foo.py:1:2: DEP001 foo imported but missing from the dependency definitions",
        "Found 1 dependency issue.",
        "\nFor more information, see the documentation: https://fpgmaas.github.io/deptry/",
    ]


def test_logging_number_none(caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        TextReporter([]).report()

    assert caplog.messages == [
        "",
        "Success! No dependency issues found.",
    ]
