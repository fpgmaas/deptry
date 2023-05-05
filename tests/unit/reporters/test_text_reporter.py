from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from deptry.dependency import Dependency
from deptry.issues_finder.misplaced_dev import MisplacedDevDependenciesFinder
from deptry.issues_finder.missing import MissingDependenciesFinder
from deptry.issues_finder.obsolete import ObsoleteDependenciesFinder
from deptry.issues_finder.transitive import TransitiveDependenciesFinder
from deptry.module import Module
from deptry.reporters import TextReporter
from deptry.violation import Violation

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture


def test_logging_number_multiple(caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        issues = {
            "missing": [Violation(MissingDependenciesFinder, Module("foo", package="foo_package"))],
            "obsolete": [Violation(ObsoleteDependenciesFinder, Dependency("foo", Path("pyproject.toml")))],
            "transitive": [Violation(TransitiveDependenciesFinder, Module("foo", package="foo_package"))],
            "misplaced_dev": [Violation(MisplacedDevDependenciesFinder, Module("foo", package="foo_package"))],
        }
        TextReporter(issues).report()

    assert "There were 4 dependency issues found" in caplog.text
    assert "The project contains obsolete dependencies" in caplog.text
    assert "There are dependencies missing from the project's list of dependencies" in caplog.text
    assert "There are transitive dependencies that should be explicitly defined as dependencies" in caplog.text
    assert "There are imported modules from development dependencies detected" in caplog.text
    assert "For more information, see the documentation" in caplog.text


def test_logging_number_single(caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        issues = {"missing": [Violation(MissingDependenciesFinder, Module("foo", package="foo_package"))]}
        TextReporter(issues).report()

    assert "There was 1 dependency issue found" in caplog.text


def test_logging_number_none(caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        issues: dict[str, list[Violation]] = {"missing": []}
        TextReporter(issues).report()

    assert "No dependency issues found" in caplog.text
    assert "There were 4 dependency issues found" not in caplog.text
    assert "The project contains obsolete dependencies" not in caplog.text
    assert "There are dependencies missing from the project's list of dependencies" not in caplog.text
    assert "There are transitive dependencies that should be explicitly defined as dependencies" not in caplog.text
    assert "There are imported modules from development dependencies detected" not in caplog.text
    assert "For more information, see the documentation" not in caplog.text
