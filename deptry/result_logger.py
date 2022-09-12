import logging
import sys
from typing import Dict, List


class ResultLogger:
    """
    Display the issues to the user, and return exit-status 0 or 1 depending on if any issues were found.
    """

    def __init__(self, issues: Dict[str, List[str]]):
        self.issues = issues

    def log_and_exit(self):
        issue_found = False
        if "obsolete" in self.issues and self.issues["obsolete"]:
            issue_found = True
            self._log_obsolete_dependencies(self.issues["obsolete"])
        if "missing" in self.issues and self.issues["missing"]:
            issue_found = True
            self._log_missing_dependencies(self.issues["missing"])
        if "transitive" in self.issues and self.issues["transitive"]:
            issue_found = True
            self._log_transitive_dependencies(self.issues["transitive"])
        if "misplaced_dev" in self.issues and self.issues["misplaced_dev"]:
            issue_found = True
            self._log_misplaced_develop_dependencies(self.issues["misplaced_dev"])

        if issue_found:
            self._log_additional_info()
            sys.exit(1)
        else:
            # TODO: adapt message below; e.g. if only checking for obsolete and transitive, display 'No obsolete or transitive dependencies found' etc
            logging.info("Success! No obsolete, missing, or transitive dependencies found.")
            sys.exit(0)

    def _log_obsolete_dependencies(self, dependencies: List[str], sep="\n\t") -> None:
        logging.info("\n-----------------------------------------------------\n")
        logging.info(f"The project contains obsolete dependencies:\n{sep}{sep.join(sorted(dependencies))}\n")
        logging.info(
            """Consider removing them from your project's dependencies. If a package is used for development purposes, you should add it to your development dependencies instead."""
        )

    def _log_missing_dependencies(self, dependencies: List[str], sep="\n\t") -> None:
        logging.info("\n-----------------------------------------------------\n")
        logging.info(
            f"There are dependencies missing from the project's list of dependencies:\n{sep}{sep.join(sorted(dependencies))}\n"
        )
        logging.info("""Consider adding them to your project's dependencies. """)

    def _log_transitive_dependencies(self, dependencies: List[str], sep="\n\t") -> None:
        logging.info("\n-----------------------------------------------------\n")
        logging.info(
            f"There are transitive dependencies that should be explicitly defined as dependencies:\n{sep}{sep.join(sorted(dependencies))}\n"
        )
        logging.info("""They are currently imported but not specified directly as your project's dependencies.""")

    def _log_misplaced_develop_dependencies(self, dependencies: List[str], sep="\n\t") -> None:
        logging.info("\n-----------------------------------------------------\n")
        logging.info(
            f"There are imported modules from development dependencies detected:\n{sep}{sep.join(sorted(dependencies))}\n"
        )
        logging.info(
            """Consider moving them to your project's 'regular' dependencies. If this is not correct and the dependencies listed above are indeed development dependencies, it's likely that files were scanned that are only used for development purposes. Run `deptry -v .` to see a list of scanned files."""
        )

    def _log_additional_info(self):
        logging.info("\n-----------------------------------------------------\n")
        logging.info(
            """Dependencies and directories can be ignored by passing additional command-line arguments. See `deptry --help` for more details.
Alternatively, deptry can be configured through `pyproject.toml`. An example:

    ```
    [tool.deptry]
    ignore_obsolete = [
    'foo'
    ]
    ignore_missing = [
    'bar'
    ]
    ignore_transitive = [
    'baz'
    ]
    exclude = [
    'venv','.venv', 'tests', 'setup.py', 'docs'
    ]
    ```

For more information, see the documentation: https://fpgmaas.github.io/deptry/
If you have encountered a bug, have a feature request or if you have any other feedback, please file a bug report at https://github.com/fpgmaas/deptry/issues/new/choose
"""
        )
