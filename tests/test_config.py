from __future__ import annotations

import logging
from pathlib import Path

import click
from _pytest.logging import LogCaptureFixture

from deptry.config import read_configuration_from_pyproject_toml
from tests.utils import run_within_dir


def test_read_configuration_from_pyproject_toml_exists(tmp_path: Path) -> None:
    click_context = click.Context(
        click.Command(""),
        default_map={
            "exclude": ["bar"],
            "extend_exclude": ["foo"],
            "ignore_notebooks": False,
            "ignore_obsolete": ["baz", "bar"],
            "ignore_missing": [],
            "ignore_misplaced_dev": [],
            "ignore_transitive": [],
            "skip_obsolete": False,
            "skip_missing": False,
            "skip_transitive": False,
            "skip_misplaced_dev": False,
            "requirements_txt": "requirements.txt",
            "requirements_txt_dev": ["requirements-dev.txt"],
        },
    )

    pyproject_toml_content = """
        [tool.deptry]
        exclude = ["foo", "bar"]
        extend_exclude = ["bar", "foo"]
        ignore_notebooks = true
        ignore_obsolete = ["foo"]
        ignore_missing = ["baz", "foobar"]
        ignore_misplaced_dev = ["barfoo"]
        ignore_transitive = ["foobaz"]
        skip_obsolete = true
        skip_missing = true
        skip_transitive = true
        skip_misplaced_dev = true
        requirements_txt = "foo.txt"
        requirements_txt_dev = ["dev.txt", "tests.txt"]
    """

    with run_within_dir(tmp_path):
        with open("pyproject.toml", "w") as f:
            f.write(pyproject_toml_content)

        assert read_configuration_from_pyproject_toml(
            click_context, click.UNPROCESSED(None), Path("pyproject.toml")
        ) == Path("pyproject.toml")

    assert click_context.default_map == {
        "exclude": ["foo", "bar"],
        "extend_exclude": ["bar", "foo"],
        "ignore_notebooks": True,
        "ignore_obsolete": ["foo"],
        "ignore_missing": ["baz", "foobar"],
        "ignore_misplaced_dev": ["barfoo"],
        "ignore_transitive": ["foobaz"],
        "skip_obsolete": True,
        "skip_missing": True,
        "skip_transitive": True,
        "skip_misplaced_dev": True,
        "requirements_txt": "foo.txt",
        "requirements_txt_dev": ["dev.txt", "tests.txt"],
    }


def test_read_configuration_from_pyproject_toml_file_not_found(caplog: LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG):
        assert read_configuration_from_pyproject_toml(
            click.Context(click.Command("")), click.UNPROCESSED(None), Path("a_non_existent_pyproject.toml")
        ) == Path("a_non_existent_pyproject.toml")

    assert "No pyproject.toml file to read configuration from." in caplog.text


def test_read_configuration_from_pyproject_toml_file_without_deptry_section(
    caplog: LogCaptureFixture, tmp_path: Path
) -> None:
    pyproject_toml_content = """
        [tool.something]
        exclude = ["foo", "bar"]
    """

    with run_within_dir(tmp_path):
        with open("pyproject.toml", "w") as f:
            f.write(pyproject_toml_content)

        with caplog.at_level(logging.DEBUG):
            assert read_configuration_from_pyproject_toml(
                click.Context(click.Command("")), click.UNPROCESSED(None), Path("pyproject.toml")
            ) == Path("pyproject.toml")

    assert "No configuration for deptry was found in pyproject.toml." in caplog.text
