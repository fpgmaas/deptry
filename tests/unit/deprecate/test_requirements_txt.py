from __future__ import annotations

from unittest.mock import ANY, patch

from click.testing import CliRunner

from deptry.cli import deptry
from deptry.deprecate.requirements_txt import (
    REQUIREMENTS_TXT_DEPRECATION_MESSAGE,
    REQUIREMENTS_TXT_DEV_DEPRECATION_MESSAGE,
)

DEFAULT_CORE_ARGS = {
    "root": (ANY,),
    "config": ANY,
    "no_ansi": ANY,
    "exclude": ANY,
    "extend_exclude": ANY,
    "using_default_exclude": ANY,
    "ignore_notebooks": ANY,
    "ignore": ANY,
    "per_rule_ignores": ANY,
    "known_first_party": ANY,
    "json_output": ANY,
    "package_module_name_map": ANY,
    "pep621_dev_dependency_groups": ANY,
    "using_default_requirements_files": ANY,
    "experimental_namespace_package": ANY,
}


def test_requirements_txt_deprecated() -> None:
    with patch("deptry.cli.Core") as mock_core, patch("logging.warning") as mock_warning:
        result = CliRunner().invoke(deptry, [".", "--requirements-txt", "somefile.txt"])

        assert result.exit_code == 0
        mock_warning.assert_called_once_with(REQUIREMENTS_TXT_DEPRECATION_MESSAGE)

        # Assert that Core was instantiated with the correct arguments
        mock_core.assert_called_once_with(
            **DEFAULT_CORE_ARGS,
            requirements_files=("somefile.txt",),
            requirements_files_dev=("dev-requirements.txt", "requirements-dev.txt"),
        )


def test_requirements_txt_dev_deprecated() -> None:
    with patch("deptry.cli.Core") as mock_core, patch("logging.warning") as mock_warning:
        result = CliRunner().invoke(deptry, [".", "--requirements-txt-dev", "somefile.txt"])

        assert result.exit_code == 0
        mock_warning.assert_called_once_with(REQUIREMENTS_TXT_DEV_DEPRECATION_MESSAGE)

        # Assert that Core was instantiated with the correct arguments
        mock_core.assert_called_once_with(
            **DEFAULT_CORE_ARGS, requirements_files=("requirements.txt",), requirements_files_dev=("somefile.txt",)
        )


def test_requirements_files_works_as_expected() -> None:
    with patch("deptry.cli.Core") as mock_core, patch("logging.warning") as mock_warning:
        result = CliRunner().invoke(deptry, [".", "--requirements-files", "somefile.txt"])

        assert result.exit_code == 0
        mock_warning.assert_not_called()

        # Assert that Core was instantiated with the correct arguments
        mock_core.assert_called_once_with(
            **DEFAULT_CORE_ARGS,
            requirements_files=("somefile.txt",),
            requirements_files_dev=("dev-requirements.txt", "requirements-dev.txt"),
        )


def test_requirements_files_dev_works_as_expected() -> None:
    with patch("deptry.cli.Core") as mock_core, patch("logging.warning") as mock_warning:
        result = CliRunner().invoke(deptry, [".", "--requirements-files-dev", "somefile.txt"])

        assert result.exit_code == 0
        mock_warning.assert_not_called()

        # Assert that Core was instantiated with the correct arguments
        mock_core.assert_called_once_with(
            **DEFAULT_CORE_ARGS, requirements_files=("requirements.txt",), requirements_files_dev=("somefile.txt",)
        )
