from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from deptry.reporters.base import Reporter

if TYPE_CHECKING:
    from deptry.imports.location import Location
    from deptry.violations import Violation


COLORS = {
    "BOLD": "\033[1m",
    "CYAN": "\033[36m",
    "GREEN": "\033[32m",
    "RED": "\033[31m",
    "RESET": "\033[m",
}
COLORS_NOOP = {color: "" for color in COLORS}


@dataclass
class TextReporter(Reporter):
    use_ansi: bool = True

    def report(self) -> None:
        self._log_and_exit()

    def _log_and_exit(self) -> None:
        self._log_violations(self.violations)

        self._log_total_number_of_violations_found(self.violations)

    def _log_total_number_of_violations_found(self, violations: list[Violation]) -> None:
        if violations:
            logging.info(
                self._stylize(
                    "{BOLD}{RED}Found {total} dependency {issue_word}.{RESET}",
                    total=len(violations),
                    issue_word="issues" if len(violations) > 1 else "issue",
                )
            )
            logging.info("\nFor more information, see the documentation: https://fpgmaas.github.io/deptry/")
        else:
            logging.info(self._stylize("{BOLD}{GREEN}Success! No dependency issues found.{RESET}"))

    def _log_violations(self, violations: list[Violation]) -> None:
        logging.info("")

        for violation in violations:
            logging.info(self._format_error(violation))

    def _format_error(self, violation: Violation) -> str:
        return self._stylize(
            "{location}{CYAN}:{RESET} {BOLD}{RED}{error_code}{RESET} {error_message}",
            location=self._format_location(violation.location),
            error_code=violation.error_code,
            error_message=violation.get_error_message(),
        )

    def _format_location(self, location: Location) -> str:
        if location.line is not None and location.column is not None:
            return self._stylize(
                "{BOLD}{file}{RESET}{CYAN}:{RESET}{line}{CYAN}:{RESET}{column}",
                file=location.file,
                line=location.line,
                column=location.column,
            )
        return self._stylize("{BOLD}{file}{RESET}", file=location.file)

    def _stylize(self, text: str, **kwargs: Any) -> str:
        return text.format(**kwargs, **self._get_colors())

    def _get_colors(self) -> dict[str, str]:
        return COLORS if self.use_ansi else COLORS_NOOP
