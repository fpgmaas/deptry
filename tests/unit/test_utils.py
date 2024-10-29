from __future__ import annotations

from pathlib import Path

import pytest

from deptry.exceptions import PyprojectFileNotFoundError
from deptry.utils import load_pyproject_toml
from tests.utils import run_within_dir


def test_load_pyproject_toml(tmp_path: Path) -> None:
    pyproject_toml = """\
[project]
name = "foo"
dependencies = ["bar", "baz>=20.9",]

[dependency-groups]
dev = ["foobar", "foobaz"]
"""
    with run_within_dir(tmp_path):
        with Path("pyproject.toml").open("w") as f:
            f.write(pyproject_toml)

        assert load_pyproject_toml(Path("pyproject.toml")) == {
            "project": {
                "name": "foo",
                "dependencies": ["bar", "baz>=20.9"],
            },
            "dependency-groups": {
                "dev": ["foobar", "foobaz"],
            },
        }


def test_load_pyproject_toml_not_found(tmp_path: Path) -> None:
    with run_within_dir(tmp_path), pytest.raises(PyprojectFileNotFoundError):
        load_pyproject_toml(Path("non_existing_pyproject.toml"))
