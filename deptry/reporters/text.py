from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from deptry.module import Module
from deptry.reporters.base import Reporter

if TYPE_CHECKING:
    from deptry.violation import Violation


@dataclass
class TextReporter(Reporter):
    def report(self) -> None:
        self._log_and_exit()

    def _log_and_exit(self) -> None:
        total_issues_found = sum([len(v) for k, v in self.issues.items()])
        self._log_total_number_of_issues_found(total_issues_found)
        if "obsolete" in self.issues and self.issues["obsolete"]:
            self._log_obsolete_dependencies(self.issues["obsolete"])
        if "missing" in self.issues and self.issues["missing"]:
            self._log_missing_dependencies(self.issues["missing"])
        if "transitive" in self.issues and self.issues["transitive"]:
            self._log_transitive_dependencies(self.issues["transitive"])
        if "misplaced_dev" in self.issues and self.issues["misplaced_dev"]:
            self._log_misplaced_develop_dependencies(self.issues["misplaced_dev"])
        if total_issues_found > 0:
            self._log_additional_info()

    @staticmethod
    def _log_total_number_of_issues_found(number: int) -> None:
        if number == 0:
            logging.info("Success! No dependency issues found.")
        elif number == 1:
            logging.info("There was 1 dependency issue found.")
        else:
            logging.info(f"There were {number} dependency issues found.")

    def _log_obsolete_dependencies(self, violations: list[Violation], sep: str = "\n\t") -> None:
        logging.info("\n-----------------------------------------------------\n")
        logging.info(
            "The project contains obsolete"
            f" dependencies:\n{sep}{sep.join(sorted([violation.issue.name for violation in violations]))}\n"
        )
        logging.info(
            """Consider removing them from your project's dependencies. If a package is used for development purposes, you should add it to your development dependencies instead."""
        )

    def _log_missing_dependencies(self, violations: list[Violation], sep: str = "\n\t") -> None:
        logging.info("\n-----------------------------------------------------\n")
        logging.info(
            "There are dependencies missing from the project's list of"
            f" dependencies:\n{sep}{sep.join(sorted([violation.issue.name for violation in violations]))}\n"
        )
        logging.info("""Consider adding them to your project's dependencies. """)

    def _log_transitive_dependencies(self, violations: list[Violation], sep: str = "\n\t") -> None:
        sorted_dependencies = []

        for violation in violations:
            # `violations` only contain transitive dependency violations, which are always `Module` that always have a
            # non-null `package` attribute.
            module = cast(Module, violation.issue)
            package_name = cast(str, module.package)
            sorted_dependencies.append(package_name)

        logging.info("\n-----------------------------------------------------\n")
        logging.info(
            "There are transitive dependencies that should be explicitly defined as"
            f" dependencies:\n{sep}{sep.join(sorted(sorted_dependencies))}\n"
        )
        logging.info("""They are currently imported but not specified directly as your project's dependencies.""")

    def _log_misplaced_develop_dependencies(self, violations: list[Violation], sep: str = "\n\t") -> None:
        logging.info("\n-----------------------------------------------------\n")
        logging.info(
            "There are imported modules from development dependencies"
            f" detected:\n{sep}{sep.join(sorted([violation.issue.name for violation in violations]))}\n"
        )
        logging.info(
            """Consider moving them to your project's 'regular' dependencies. If this is not correct and the dependencies listed above are indeed development dependencies, it's likely that files were scanned that are only used for development purposes. Run `deptry -v .` to see a list of scanned files."""
        )

    def _log_additional_info(self) -> None:
        logging.info("\n-----------------------------------------------------\n")
        logging.info(
            """Dependencies and directories can be ignored by passing additional command-line arguments. See `deptry --help` for more details.
Alternatively, deptry can be configured through `pyproject.toml`. An example:

    ```
    [tool.deptry]
    ignore_obsolete = [
        "foo"
    ]
    ignore_missing = [
        "bar"
    ]
    ignore_transitive = [
        "baz"
    ]
    extend_exclude = [
        ".*/foo/",
        "bar/baz.py"
    ]
    ```

For more information, see the documentation: https://fpgmaas.github.io/deptry/
If you have encountered a bug, have a feature request or if you have any other feedback, please file a bug report at https://github.com/fpgmaas/deptry/issues/new/choose
"""
        )
