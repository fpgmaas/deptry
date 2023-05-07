from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from deptry.reporters.base import Reporter

if TYPE_CHECKING:
    from deptry.violations import Violation


@dataclass
class TextReporter(Reporter):
    def report(self) -> None:
        self._log_and_exit()

    def _log_and_exit(self) -> None:
        self._log_violations(self.violations)

        self._log_total_number_of_violations_found(self.violations)

    @staticmethod
    def _log_total_number_of_violations_found(violations: list[Violation]) -> None:
        if violations:
            logging.info(f"Found {len(violations)} dependency {'issues' if len(violations) > 1 else 'issue'}.")
            logging.info("\nFor more information, see the documentation: https://fpgmaas.github.io/deptry/")
        else:
            logging.info("Success! No dependency issues found.")

    def _log_violations(self, violations: list[Violation]) -> None:
        logging.info("")

        for violation in violations:
            logging.info(self._format_error(violation))

    @classmethod
    def _format_error(cls, violation: Violation) -> str:
        return f"{(violation.location.format_for_terminal())}: {violation.error_code} {violation.get_error_message()}"
