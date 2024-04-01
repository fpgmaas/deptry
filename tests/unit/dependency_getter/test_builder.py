from __future__ import annotations

import re
from pathlib import Path

import pytest

from deptry.dependency_getter.builder import DependencyGetterBuilder
from deptry.dependency_getter.pdm import PDMDependencyGetter
from deptry.dependency_getter.pep_621 import PEP621DependencyGetter
from deptry.dependency_getter.poetry import PoetryDependencyGetter
from deptry.dependency_getter.requirements_files import RequirementsTxtDependencyGetter
from deptry.exceptions import DependencySpecificationNotFoundError
from tests.utils import run_within_dir


def test_poetry(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        pyproject_toml_path = Path("pyproject.toml")

        with pyproject_toml_path.open("w") as f:
            f.write('[tool.poetry.dependencies]\nfake = "10"')

        spec = DependencyGetterBuilder(pyproject_toml_path).build()
        assert isinstance(spec, PoetryDependencyGetter)


def test_pdm_with_dev_dependencies(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        pyproject_toml_path = Path("pyproject.toml")

        with pyproject_toml_path.open("w") as f:
            f.write(
                '[project]\ndependencies=["foo"]\n[tool.pdm]\nversion = {source ='
                ' "scm"}\n[tool.pdm.dev-dependencies]\ngroup=["bar"]'
            )

        spec = DependencyGetterBuilder(pyproject_toml_path).build()
        assert isinstance(spec, PDMDependencyGetter)


def test_pdm_without_dev_dependencies(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        pyproject_toml_path = Path("pyproject.toml")

        with pyproject_toml_path.open("w") as f:
            f.write('[project]\ndependencies=["foo"]\n[tool.pdm]\nversion = {source = "scm"}')

        spec = DependencyGetterBuilder(pyproject_toml_path).build()
        assert isinstance(spec, PEP621DependencyGetter)


def test_pep_621(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        pyproject_toml_path = Path("pyproject.toml")

        with pyproject_toml_path.open("w") as f:
            f.write('[project]\ndependencies=["foo"]')

        spec = DependencyGetterBuilder(pyproject_toml_path).build()
        assert isinstance(spec, PEP621DependencyGetter)


def test_both(tmp_path: Path) -> None:
    """
    If both are found, result should be 'poetry'
    """

    with run_within_dir(tmp_path):
        pyproject_toml_path = Path("pyproject.toml")

        with pyproject_toml_path.open("w") as f:
            f.write('[tool.poetry.dependencies]\nfake = "10"')

        with Path("requirements.txt").open("w") as f:
            f.write('foo >= "1.0"')

        spec = DependencyGetterBuilder(pyproject_toml_path).build()
        assert isinstance(spec, PoetryDependencyGetter)


def test_requirements_files(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        with Path("requirements.txt").open("w") as f:
            f.write('foo >= "1.0"')

        spec = DependencyGetterBuilder(Path("pyproject.toml"), requirements_files=("requirements.txt",)).build()
        assert isinstance(spec, RequirementsTxtDependencyGetter)


def test_requirements_files_with_argument_not_root_directory(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        Path("req").mkdir()

        with Path("req/req.txt").open("w") as f:
            f.write('foo >= "1.0"')

        spec = DependencyGetterBuilder(Path("pyproject.toml"), requirements_files=("req/req.txt",)).build()
        assert isinstance(spec, RequirementsTxtDependencyGetter)


def test_dependency_specification_not_found_raises_exception(tmp_path: Path) -> None:
    with run_within_dir(tmp_path), pytest.raises(
        DependencySpecificationNotFoundError,
        match=re.escape(
            "No file called 'pyproject.toml' with a [tool.poetry.dependencies], [tool.pdm] or [project] section or"
            " file(s) called 'req/req.txt' found. Exiting."
        ),
    ):
        DependencyGetterBuilder(Path("pyproject.toml"), requirements_files=("req/req.txt",)).build()
