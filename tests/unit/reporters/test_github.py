from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from deptry.imports.location import Location
from deptry.module import Module
from deptry.reporters.github import GithubReporter, _build_workflow_command, _escape
from deptry.violations import DEP001MissingDependencyViolation

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture

    from deptry.violations import Violation

# Extract violation instance as a parameter
violation_instance = DEP001MissingDependencyViolation(
    Module("foo", package="foo-package"), Location(Path("foo.py"), 1, 2)
)

expected_warning = _build_workflow_command(
    "warning",
    "DEP001",
    "'foo' imported but missing from the dependency definitions",
    "foo.py",
    line=1,
    column=2,
)

expected_error = _build_workflow_command(
    "error", "DEP001", "'foo' imported but missing from the dependency definitions", "foo.py", line=1, column=2
)


@pytest.mark.parametrize(
    ("violation", "warning_ids", "expected"),
    [
        (violation_instance, ["DEP001"], expected_warning),
        (violation_instance, [], expected_error),
    ],
)
def test_github_annotation(
    caplog: LogCaptureFixture, violation: Violation, warning_ids: tuple[str, ...], expected: str
) -> None:
    reporter = GithubReporter(violations=[violation], warning_ids=warning_ids)

    with caplog.at_level(logging.INFO):
        reporter.report()

    assert expected in caplog.text.strip()


def test_build_workflow_command_escaping() -> None:
    # Directly test _build_workflow_command with characters needing escape.
    message = "Error % occurred\r\nNew line"
    escaped_message = _escape(message)
    command = _build_workflow_command("warning", "TEST", message, "file.py", line=10, column=2)
    assert "::warning file=file.py,line=10,col=2,title=TEST::" in command
    assert escaped_message in command
