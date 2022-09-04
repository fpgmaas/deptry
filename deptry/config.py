import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import toml
from typeguard import TypeCheckError, check_type

DEFAULTS = {"ignore_dependencies": None, "ignore_directories": [".venv"], "ignore_notebooks": False}


class Config:
    """
    Create configuration for deptry. First the configuration parameters are set to the defaults. If configuration is found in pyproject.toml,
    this overrides the defaults. CLI arguments have highest priority, so if they are provided, they override the values set by
    either the defaults or pyproject.toml.
    """

    def __init__(
        self,
        ignore_dependencies: Optional[List[str]],
        ignore_directories: Optional[List[str]],
        ignore_notebooks: Optional[bool],
    ) -> None:
        self._set_defaults()
        self._override_config_with_pyproject_toml()
        self._override_config_with_cli_arguments(ignore_dependencies, ignore_directories, ignore_notebooks)

    def _set_defaults(self) -> None:
        self.ignore_dependencies = DEFAULTS["ignore_dependencies"]
        self.ignore_directories = DEFAULTS["ignore_directories"]
        self.ignore_notebooks = DEFAULTS["ignore_notebooks"]

    def _override_config_with_pyproject_toml(self) -> None:  # noqa: C901

        pyproject_toml_config = self._read_configuration_from_pyproject_toml()

        if pyproject_toml_config:

            if "ignore_dependencies" in pyproject_toml_config:
                value = pyproject_toml_config["ignore_dependencies"]
                try:
                    check_type(value, List[str])
                except TypeCheckError:
                    raise TypeCheckError(
                        "Invalid argument supplied for `ignore_dependencies` in pyproject.toml. Should be a list of strings."
                    )
                self.ignore_dependencies = value
                self._log_changed_by_pyproject_toml("ignore_dependencies", value)

            if "ignore_directories" in pyproject_toml_config:
                value = pyproject_toml_config["ignore_directories"]
                try:
                    check_type(value, List[str])
                except TypeCheckError:
                    raise TypeCheckError(
                        "Invalid argument supplied for `ignore_notebooks` in pyproject.toml. Should be a list of strings."
                    )
                self.ignore_directories = value
                self._log_changed_by_pyproject_toml("ignore_directories", value)

            if "ignore_notebooks" in pyproject_toml_config:
                value = pyproject_toml_config["ignore_notebooks"]
                try:
                    check_type(value, bool)
                except TypeCheckError:
                    raise TypeCheckError(
                        "Invalid argument supplied for `ignore_notebooks` in pyproject.toml. Should be boolean."
                    )
                self.ignore_notebooks = value
                self._log_changed_by_pyproject_toml("ignore_notebooks", value)

    def _override_config_with_cli_arguments(
        self,
        ignore_dependencies: Optional[List[str]],
        ignore_directories: Optional[List[str]],
        ignore_notebooks: Optional[bool],
    ) -> None:

        if ignore_dependencies:
            self.ignore_dependencies = ignore_dependencies
            self._log_changed_by_command_line_argument("ignore_dependencies", ignore_dependencies)

        if ignore_directories:
            self.ignore_directories = ignore_directories
            self._log_changed_by_command_line_argument("ignore_directories", ignore_directories)

        if ignore_notebooks:
            self.ignore_notebooks = ignore_notebooks
            self._log_changed_by_command_line_argument("ignore_notebooks", ignore_notebooks)

    def _read_configuration_from_pyproject_toml(self) -> Optional[Dict]:
        try:
            pyproject_text = Path("./pyproject.toml").read_text()
            pyproject_data = toml.loads(pyproject_text)
            return pyproject_data["tool"]["deptry"]
        except:  # noqa
            logging.debug("No configuration for deptry was found in pyproject.toml.")
            return None

    @staticmethod
    def _log_changed_by_pyproject_toml(argument: str, value: Any):
        logging.debug(f"Argument {argument} set to {str(value)} by pyproject.toml")

    @staticmethod
    def _log_changed_by_command_line_argument(argument: str, value: Any):
        logging.debug(f"Argument {argument} set to {str(value)} by pyproject.toml")
