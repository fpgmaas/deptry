from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from deptry.reporters.base import Reporter

if TYPE_CHECKING:
    from deptry.violations import Violation


@dataclass
class GithubReporter(Reporter):
    warning_ids: list[str] = field(default_factory=list)  # list of error codes to print as warnings

    def report(self) -> None:
        self._log_and_exit()

    def _log_and_exit(self) -> None:
        self._log_violations(self.violations)

    def _log_violations(self, violations: list[Violation]) -> None:
        for violation in violations:
            self._print_github_annotation(violation)

    def _print_github_annotation(self, violation: Violation) -> None:
        annotation_severity = "warning" if violation.error_code in self.warning_ids else "error"
        file_name = violation.location.file
        if violation.location.line is not None and violation.location.column is not None:
            ret = _build_workflow_command(
                annotation_severity,
                str(file_name),
                violation.location.line,
                column=violation.location.column,
                title=violation.error_code,
                message=violation.get_error_message(),
            )
            logging.info(ret)


def _build_workflow_command(
    command_name: str,
    file: str,
    line: int,
    end_line: int | None = None,
    column: int | None = None,
    end_column: int | None = None,
    title: str | None = None,
    message: str | None = None,
) -> str:
    """Build a command to annotate a workflow."""
    result = f"::{command_name} "

    entries = [
        ("file", file),
        ("line", line),
        ("endLine", end_line),
        ("col", column),
        ("endColumn", end_column),
        ("title", title),
    ]

    result = result + ",".join(f"{k}={v}" for k, v in entries if v is not None)

    if message is not None:
        result = result + "::" + _escape(message)

    return result


def _escape(s: str) -> str:
    return s.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
