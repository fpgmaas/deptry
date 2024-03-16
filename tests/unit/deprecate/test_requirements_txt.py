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
}


def test_requirements_txt_deprecated():
    with patch("deptry.cli.Core") as mock_core, patch("logging.warning") as mock_warning:
        result = CliRunner().invoke(deptry, [".", "--requirements-txt", "somefile.txt"])

        assert result.exit_code == 0
        mock_warning.assert_called_once_with(REQUIREMENTS_TXT_DEPRECATION_MESSAGE)

        # Assert that Core was instantiated with the correct arguments
        mock_core.assert_called_once_with(
            **DEFAULT_CORE_ARGS,
            requirements_file=("somefile.txt",),
            requirements_file_dev=("dev-requirements.txt", "requirements-dev.txt"),
        )


def test_requirements_txt_dev_deprecated():
    with patch("deptry.cli.Core") as mock_core, patch("logging.warning") as mock_warning:
        result = CliRunner().invoke(deptry, [".", "--requirements-txt-dev", "somefile.txt"])

        assert result.exit_code == 0
        mock_warning.assert_called_once_with(REQUIREMENTS_TXT_DEV_DEPRECATION_MESSAGE)

        # Assert that Core was instantiated with the correct arguments
        mock_core.assert_called_once_with(
            **DEFAULT_CORE_ARGS, requirements_file=("requirements.txt",), requirements_file_dev=("somefile.txt",)
        )


def test_requirements_file_works_as_expected():
    with patch("deptry.cli.Core") as mock_core, patch("logging.warning") as mock_warning:
        result = CliRunner().invoke(deptry, [".", "--requirements-file", "somefile.txt"])

        assert result.exit_code == 0
        mock_warning.assert_not_called()

        # Assert that Core was instantiated with the correct arguments
        mock_core.assert_called_once_with(
            **DEFAULT_CORE_ARGS,
            requirements_file=("somefile.txt",),
            requirements_file_dev=("dev-requirements.txt", "requirements-dev.txt"),
        )


def test_requirements_file_dev_works_as_expected():
    with patch("deptry.cli.Core") as mock_core, patch("logging.warning") as mock_warning:
        result = CliRunner().invoke(deptry, [".", "--requirements-file-dev", "somefile.txt"])

        assert result.exit_code == 0
        mock_warning.assert_not_called()

        # Assert that Core was instantiated with the correct arguments
        mock_core.assert_called_once_with(
            **DEFAULT_CORE_ARGS, requirements_file=("requirements.txt",), requirements_file_dev=("somefile.txt",)
        )
