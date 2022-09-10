import logging
from typing import Any, Dict, List, Optional

from deptry.utils import load_pyproject_toml

DEFAULTS = {
    "ignore_obsolete": [],
    "ignore_missing": [],
    "ignore_transitive": [],
    "ignore_misplaced_dev": [],
    "exclude": [".venv", "tests"],
    "extend_exclude": [],
    "ignore_notebooks": False,
    "skip_obsolete": False,
    "skip_missing": False,
    "skip_transitive": False,
    "skip_misplaced_dev": False,
}


class Config:
    """
    Create configuration for deptry. First the configuration parameters are set to the defaults. If configuration is found in pyproject.toml,
    this overrides the defaults. CLI arguments have highest priority, so if they are provided, they override the values set by
    either the defaults or pyproject.toml.
    """

    def __init__(
        self,
        ignore_obsolete: Optional[List[str]],
        ignore_missing: Optional[List[str]],
        ignore_transitive: Optional[List[str]],
        ignore_misplaced_dev: Optional[List[str]],
        skip_obsolete: Optional[bool],
        skip_missing: Optional[bool],
        skip_transitive: Optional[bool],
        skip_misplaced_dev: Optional[bool],
        exclude: Optional[List[str]],
        extend_exclude: Optional[List[str]],
        ignore_notebooks: Optional[bool],
    ) -> None:
        self._set_defaults()
        self._override_config_with_pyproject_toml()
        self._override_config_with_cli_arguments(
            ignore_obsolete=ignore_obsolete,
            ignore_missing=ignore_missing,
            ignore_transitive=ignore_transitive,
            ignore_misplaced_dev=ignore_misplaced_dev,
            exclude=exclude,
            extend_exclude=extend_exclude,
            ignore_notebooks=ignore_notebooks,
            skip_obsolete=skip_obsolete,
            skip_missing=skip_missing,
            skip_transitive=skip_transitive,
            skip_misplaced_dev=skip_misplaced_dev,
        )

    def _set_defaults(self) -> None:
        self.ignore_obsolete = DEFAULTS["ignore_obsolete"]
        self.ignore_missing = DEFAULTS["ignore_missing"]
        self.ignore_transitive = DEFAULTS["ignore_transitive"]
        self.ignore_misplaced_dev = DEFAULTS["ignore_misplaced_dev"]
        self.exclude = DEFAULTS["exclude"]
        self.extend_exclude = DEFAULTS["extend_exclude"]
        self.ignore_notebooks = DEFAULTS["ignore_notebooks"]
        self.skip_obsolete = DEFAULTS["skip_obsolete"]
        self.skip_missing = DEFAULTS["skip_missing"]
        self.skip_transitive = DEFAULTS["skip_transitive"]
        self.skip_misplaced_dev = DEFAULTS["skip_misplaced_dev"]

    def _override_config_with_pyproject_toml(self) -> None:
        pyproject_toml_config = self._read_configuration_from_pyproject_toml()
        if pyproject_toml_config:
            self._override_with_toml_argument("ignore_obsolete", pyproject_toml_config)
            self._override_with_toml_argument("ignore_missing", pyproject_toml_config)
            self._override_with_toml_argument("ignore_transitive", pyproject_toml_config)
            self._override_with_toml_argument("ignore_misplaced_dev", pyproject_toml_config)
            self._override_with_toml_argument("skip_missing", pyproject_toml_config)
            self._override_with_toml_argument("skip_obsolete", pyproject_toml_config)
            self._override_with_toml_argument("skip_transitive", pyproject_toml_config)
            self._override_with_toml_argument("skip_misplaced_dev", pyproject_toml_config)
            self._override_with_toml_argument("exclude", pyproject_toml_config)
            self._override_with_toml_argument("extend_exclude", pyproject_toml_config)
            self._override_with_toml_argument("ignore_notebooks", pyproject_toml_config)

    def _read_configuration_from_pyproject_toml(self) -> Optional[Dict]:
        pyproject_data = load_pyproject_toml()
        try:
            return pyproject_data["tool"]["deptry"]
        except KeyError:  # noqa
            logging.debug("No configuration for deptry was found in pyproject.toml.")
            return None

    def _override_with_toml_argument(self, argument: str, pyproject_toml_config: Dict) -> None:
        """
        If argument is found in pyproject.toml, override the default argument with the found value.
        """
        if argument in pyproject_toml_config:
            value = pyproject_toml_config[argument]
            setattr(self, argument, value)
            self._log_changed_by_pyproject_toml(argument, value)

    def _override_config_with_cli_arguments(  # noqa
        self,
        ignore_obsolete: Optional[List[str]],
        ignore_missing: Optional[List[str]],
        ignore_transitive: Optional[List[str]],
        ignore_misplaced_dev: Optional[List[str]],
        exclude: Optional[List[str]],
        extend_exclude: Optional[List[str]],
        ignore_notebooks: Optional[bool],
        skip_obsolete: Optional[bool],
        skip_missing: Optional[bool],
        skip_transitive: Optional[bool],
        skip_misplaced_dev: Optional[bool],
    ) -> None:

        if ignore_obsolete:
            self.ignore_obsolete = ignore_obsolete
            self._log_changed_by_command_line_argument("ignore_obsolete", ignore_obsolete)

        if ignore_missing:
            self.ignore_missing = ignore_missing
            self._log_changed_by_command_line_argument("ignore_missing", ignore_missing)

        if ignore_transitive:
            self.ignore_transitive = ignore_transitive
            self._log_changed_by_command_line_argument("ignore_transitive", ignore_transitive)

        if ignore_misplaced_dev:
            self.ignore_misplaced_dev = ignore_misplaced_dev
            self._log_changed_by_command_line_argument("ignore_misplaced_dev", ignore_misplaced_dev)

        if skip_obsolete:
            self.skip_obsolete = skip_obsolete
            self._log_changed_by_command_line_argument("skip_obsolete", skip_obsolete)

        if skip_missing:
            self.skip_missing = skip_missing
            self._log_changed_by_command_line_argument("skip_missing", skip_missing)

        if skip_transitive:
            self.skip_transitive = skip_transitive
            self._log_changed_by_command_line_argument("skip_transitive", skip_transitive)

        if skip_misplaced_dev:
            self.skip_misplaced_dev = skip_misplaced_dev
            self._log_changed_by_command_line_argument("skip_misplaced_dev", skip_misplaced_dev)

        if exclude:
            self.exclude = exclude
            self._log_changed_by_command_line_argument("exclude", exclude)

        if extend_exclude:
            self.extend_exclude = extend_exclude
            self._log_changed_by_command_line_argument("extend_exclude", extend_exclude)

        if ignore_notebooks:
            self.ignore_notebooks = ignore_notebooks
            self._log_changed_by_command_line_argument("ignore_notebooks", ignore_notebooks)

    @staticmethod
    def _log_changed_by_pyproject_toml(argument: str, value: Any) -> None:
        logging.debug(f"Argument {argument} set to {str(value)} by pyproject.toml")

    @staticmethod
    def _log_changed_by_command_line_argument(argument: str, value: Any) -> None:
        logging.debug(f"Argument {argument} set to {str(value)} by command line argument")
