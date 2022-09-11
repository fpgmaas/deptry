import logging
import os
from typing import Any, Dict

from deptry.cli_defaults import DEFAULTS
from deptry.utils import load_pyproject_toml


class Config:
    """
    Create configuration for deptry. First the configuration parameters are set to the defaults. If configuration is found in pyproject.toml,
    this overrides the defaults. CLI arguments have highest priority, so if they are provided, they override the values set by
    either the defaults or pyproject.toml.
    """

    def __init__(
        self,
        ignore_obsolete: str = None,
        ignore_missing: str = None,
        ignore_transitive: str = None,
        ignore_misplaced_dev: str = None,
        skip_obsolete: bool = None,
        skip_missing: bool = None,
        skip_transitive: bool = None,
        skip_misplaced_dev: bool = None,
        exclude: str = None,
        extend_exclude: str = None,
        ignore_notebooks: bool = None,
        requirements_txt: str = None,
        requirements_txt_dev: str = None,
    ) -> None:

        self.pyproject_data = self._read_configuration_from_pyproject_toml()
        self._set_string_to_list_config("ignore_obsolete", ignore_obsolete)
        self._set_string_to_list_config("ignore_missing", ignore_missing)
        self._set_string_to_list_config("ignore_transitive", ignore_transitive)
        self._set_string_to_list_config("ignore_misplaced_dev", ignore_misplaced_dev)
        self._set_string_to_list_config("exclude", exclude)
        self._set_string_to_list_config("extend_exclude", extend_exclude)
        self._set_bool_config("skip_obsolete", skip_obsolete)
        self._set_bool_config("skip_missing", skip_missing)
        self._set_bool_config("skip_transitive", skip_transitive)
        self._set_bool_config("skip_misplaced_dev", skip_misplaced_dev)
        self._set_bool_config("ignore_notebooks", ignore_notebooks)
        self._set_string_config("requirements_txt", requirements_txt)
        self._set_string_to_list_config("requirements_txt_dev", requirements_txt_dev)

    def _set_string_to_list_config(self, attribute: str, cli_value: str):
        """
        Set configuration for arguments that are supplied as strings in the CLI, but should be converted to a list.
        """
        self._set_default_string_to_list(attribute)
        self._override_with_toml_argument(attribute)
        self._override_with_cli_argument_string_to_list(attribute, cli_value)

    def _set_bool_config(self, attribute: str, cli_value: str):
        """
        Set configuration for boolean arguments.
        """
        self._set_default_boolean(attribute)
        self._override_with_toml_argument(attribute)
        self._override_with_cli_argument_boolean(attribute, cli_value)

    def _set_string_config(self, attribute: str, cli_value: str):
        """
        Set configuration for arguments that are supplied as strings in the CLI, but should be converted to a list.
        """
        self._set_default_string(attribute)
        self._override_with_toml_argument(attribute)
        self._override_with_cli_argument_string(attribute, cli_value)

    def _set_default_string_to_list(self, attribute: str):
        setattr(self, attribute, self._comma_separated_string_to_list(DEFAULTS[attribute]))

    def _set_default_boolean(self, attribute: str):
        setattr(self, attribute, DEFAULTS[attribute])

    def _set_default_string(self, attribute: str):
        setattr(self, attribute, DEFAULTS[attribute])

    def _override_with_cli_argument_string_to_list(self, attribute, value):
        if value and not value == DEFAULTS[attribute]:
            value_as_list = self._comma_separated_string_to_list(value)
            self._log_changed_by_command_line_argument(attribute, value_as_list)
            setattr(self, attribute, value_as_list)

    def _override_with_cli_argument_string(self, attribute, value):
        if value and not value == DEFAULTS[attribute]:
            self._log_changed_by_command_line_argument(attribute, value)
            setattr(self, attribute, value)

    def _override_with_cli_argument_boolean(self, attribute, value):
        if value and not value == DEFAULTS[attribute]:
            self._log_changed_by_command_line_argument(attribute, value)
            setattr(self, attribute, value)

    def _override_with_toml_argument(self, argument: str) -> None:
        """
        If argument is found in pyproject.toml, override the default argument with the found value.
        """
        if self.pyproject_data and argument in self.pyproject_data:
            value = self.pyproject_data[argument]
            setattr(self, argument, value)
            self._log_changed_by_pyproject_toml(argument, value)

    def _read_configuration_from_pyproject_toml(self) -> Dict:
        if self._pyproject_toml_exists():
            pyproject_data = load_pyproject_toml()
        else:
            logging.debug("No pyproject.toml file to read configuration from.")
            return None
        try:
            return pyproject_data["tool"]["deptry"]
        except KeyError:  # noqa
            logging.debug("No configuration for deptry was found in pyproject.toml.")
            return None

    @staticmethod
    def _log_changed_by_pyproject_toml(argument: str, value: Any) -> None:
        logging.debug(f"Argument {argument} set to {str(value)} by pyproject.toml")

    @staticmethod
    def _log_changed_by_command_line_argument(argument: str, value: Any) -> None:
        logging.debug(f"Argument {argument} set to {str(value)} by command line argument")

    @staticmethod
    def _comma_separated_string_to_list(string: str):
        if len(string) > 0:
            return string.split(",")
        else:
            return []

    @staticmethod
    def _pyproject_toml_exists() -> bool:
        if "pyproject.toml" in os.listdir():
            return True
        return False
