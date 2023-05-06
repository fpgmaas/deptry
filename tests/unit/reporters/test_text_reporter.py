from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from deptry.reporters import TextReporter

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture


def test_logging_number_multiple(caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        issues = {
            "missing": ["foo"],
            "obsolete": ["foo"],
            "transitive": ["foo"],
            "misplaced_dev": ["foo"],
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
        issues = {"missing": ["foo"]}
        TextReporter(issues).report()

    assert "There was 1 dependency issue found" in caplog.text


def test_logging_number_none(caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        issues: dict[str, list[str]] = {"missing": []}
        TextReporter(issues).report()

    assert "No dependency issues found" in caplog.text
    assert "There were 4 dependency issues found" not in caplog.text
    assert "The project contains obsolete dependencies" not in caplog.text
    assert "There are dependencies missing from the project's list of dependencies" not in caplog.text
    assert "There are transitive dependencies that should be explicitly defined as dependencies" not in caplog.text
    assert "There are imported modules from development dependencies detected" not in caplog.text
    assert "For more information, see the documentation" not in caplog.text
