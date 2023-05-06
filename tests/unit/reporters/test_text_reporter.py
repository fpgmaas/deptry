from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from deptry.dependency import Dependency
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

    from deptry.violations import Violation


def test_logging_number_multiple(caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        violations: dict[str, list[Violation]] = {
            "missing": [MissingDependencyViolation(Module("foo", package="foo_package"))],
            "obsolete": [ObsoleteDependencyViolation(Dependency("foo", Path("pyproject.toml")))],
            "transitive": [TransitiveDependencyViolation(Module("foo", package="foo_package"))],
            "misplaced_dev": [MisplacedDevDependencyViolation(Module("foo", package="foo_package"))],
        }
        TextReporter(violations).report()

    assert "There were 4 dependency issues found" in caplog.text
    assert "The project contains obsolete dependencies" in caplog.text
    assert "There are dependencies missing from the project's list of dependencies" in caplog.text
    assert "There are transitive dependencies that should be explicitly defined as dependencies" in caplog.text
    assert "There are imported modules from development dependencies detected" in caplog.text
    assert "For more information, see the documentation" in caplog.text


def test_logging_number_single(caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        violations: dict[str, list[Violation]] = {
            "missing": [MissingDependencyViolation(Module("foo", package="foo_package"))]
        }
        TextReporter(violations).report()

    assert "There was 1 dependency issue found" in caplog.text


def test_logging_number_none(caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        violations: dict[str, list[Violation]] = {"missing": []}
        TextReporter(violations).report()

    assert "No dependency issues found" in caplog.text
    assert "There were 4 dependency issues found" not in caplog.text
    assert "The project contains obsolete dependencies" not in caplog.text
    assert "There are dependencies missing from the project's list of dependencies" not in caplog.text
    assert "There are transitive dependencies that should be explicitly defined as dependencies" not in caplog.text
    assert "There are imported modules from development dependencies detected" not in caplog.text
    assert "For more information, see the documentation" not in caplog.text
