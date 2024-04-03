from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from deptry.dependency import Dependency
from deptry.imports.location import Location
from deptry.module import Module
from deptry.reporters import TextReporter
from deptry.reporters.text import COLORS, COLORS_NOOP
from deptry.violations import (
    DEP001MissingDependencyViolation,
    DEP002UnusedDependencyViolation,
    DEP003TransitiveDependencyViolation,
    DEP004MisplacedDevDependencyViolation,
)
from tests.utils import stylize

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture


def test_logging_number_multiple(caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        violations = [
            DEP001MissingDependencyViolation(Module("foo", package="foo-package"), Location(Path("foo.py"), 1, 2)),
            DEP002UnusedDependencyViolation(
                Dependency("foo", Path("pyproject.toml")), Location(Path("pyproject.toml"))
            ),
            DEP003TransitiveDependencyViolation(
                Module("foo", package="foo-package"), Location(Path("foo/bar.py"), 1, 2)
            ),
            DEP004MisplacedDevDependencyViolation(Module("foo", package="foo-package"), Location(Path("foo.py"), 1, 2)),
        ]
        TextReporter(violations).report()

    assert caplog.messages == [
        (
            "Assuming the corresponding module name of package 'foo' is 'foo'. Install the package or configure a"
            " package_module_name_map entry to override this behaviour."
        ),
        "",
        stylize(
            "{BOLD}{file}{RESET}{CYAN}:{RESET}1{CYAN}:{RESET}2{CYAN}:{RESET} {BOLD}{RED}DEP001{RESET} 'foo'"
            " imported but missing from the dependency definitions",
            file=Path("foo.py"),
        ),
        stylize(
            "{BOLD}{file}{RESET}{CYAN}:{RESET} {BOLD}{RED}DEP002{RESET} 'foo' defined as a dependency but not used"
            " in the codebase",
            file=Path("pyproject.toml"),
        ),
        stylize(
            "{BOLD}{file}{RESET}{CYAN}:{RESET}1{CYAN}:{RESET}2{CYAN}:{RESET} {BOLD}{RED}DEP003{RESET} 'foo'"
            " imported but it is a transitive dependency",
            file=Path("foo/bar.py"),
        ),
        stylize(
            "{BOLD}{file}{RESET}{CYAN}:{RESET}1{CYAN}:{RESET}2{CYAN}:{RESET} {BOLD}{RED}DEP004{RESET} 'foo'"
            " imported but declared as a dev dependency",
            file=Path("foo.py"),
        ),
        stylize("{BOLD}{RED}Found 4 dependency issues.{RESET}"),
        "\nFor more information, see the documentation: https://deptry.com/",
    ]


def test_logging_number_single(caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        TextReporter([
            DEP001MissingDependencyViolation(Module("foo", package="foo-package"), Location(Path("foo.py"), 1, 2))
        ]).report()

    assert caplog.messages == [
        "",
        stylize(
            "{BOLD}{file}{RESET}{CYAN}:{RESET}1{CYAN}:{RESET}2{CYAN}:{RESET} {BOLD}{RED}DEP001{RESET} 'foo'"
            " imported but missing from the dependency definitions",
            file=Path("foo.py"),
        ),
        stylize("{BOLD}{RED}Found 1 dependency issue.{RESET}"),
        "\nFor more information, see the documentation: https://deptry.com/",
    ]


def test_logging_number_none(caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        TextReporter([]).report()

    assert caplog.messages == [
        "",
        stylize("{BOLD}{GREEN}Success! No dependency issues found.{RESET}"),
    ]


def test_logging_no_ansi(caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        violations = [
            DEP001MissingDependencyViolation(Module("foo", package="foo-package"), Location(Path("foo.py"), 1, 2)),
            DEP002UnusedDependencyViolation(
                Dependency("foo", Path("pyproject.toml")), Location(Path("pyproject.toml"))
            ),
            DEP003TransitiveDependencyViolation(
                Module("foo", package="foo-package"), Location(Path("foo/bar.py"), 1, 2)
            ),
            DEP004MisplacedDevDependencyViolation(Module("foo", package="foo-package"), Location(Path("foo.py"), 1, 2)),
        ]
        TextReporter(violations, use_ansi=False).report()

    assert caplog.messages == [
        (
            "Assuming the corresponding module name of package 'foo' is 'foo'. Install the package or configure a"
            " package_module_name_map entry to override this behaviour."
        ),
        "",
        f"{Path('foo.py')}:1:2: DEP001 'foo' imported but missing from the dependency definitions",
        f"{Path('pyproject.toml')}: DEP002 'foo' defined as a dependency but not used in the codebase",
        f"{Path('foo/bar.py')}:1:2: DEP003 'foo' imported but it is a transitive dependency",
        f"{Path('foo.py')}:1:2: DEP004 'foo' imported but declared as a dev dependency",
        "Found 4 dependency issues.",
        "\nFor more information, see the documentation: https://deptry.com/",
    ]


@pytest.mark.parametrize(
    ("use_ansi", "expected"),
    [
        (True, COLORS),
        (False, COLORS_NOOP),
    ],
)
def test__get_colors(use_ansi: bool, expected: dict[str, str]) -> None:
    assert TextReporter([], use_ansi)._get_colors() == expected
