from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from deptry.dependency_getter.builder import DependencyGetterBuilder
from deptry.dependency_getter.pep621.base import PEP621DependencyGetter
from deptry.dependency_getter.pep621.pdm import PDMDependencyGetter
from deptry.dependency_getter.pep621.poetry import PoetryDependencyGetter
from deptry.dependency_getter.pep621.uv import UvDependencyGetter
from deptry.dependency_getter.requirements_files import RequirementsTxtDependencyGetter
from deptry.exceptions import DependencySpecificationNotFoundError
from tests.utils import run_within_dir

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture


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


def test_uv_with_dev_dependencies(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        pyproject_toml_path = Path("pyproject.toml")

        with pyproject_toml_path.open("w") as f:
            f.write(
                '[project]\ndependencies=["foo"]\n[tool.uv]\ncompile-bytecode = true\n[tool.uv.dev-dependencies]\n["bar"]'
            )

        spec = DependencyGetterBuilder(pyproject_toml_path).build()
        assert isinstance(spec, UvDependencyGetter)


def test_uv_without_dev_dependencies(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        pyproject_toml_path = Path("pyproject.toml")

        with pyproject_toml_path.open("w") as f:
            f.write('[project]\ndependencies=["foo"]\n[tool.uv]\ncompile-bytecode = true')

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


def test_setuptools_dynamic_dependencies(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        with Path("requirements.txt").open("w") as f:
            f.write("foo >= 1.0")
        with Path("pyproject.toml").open("w") as f:
            f.write("""
            [build-system]
            build-backend = "setuptools.build_meta"
            [project]
            dynamic = ["dependencies"]
            [tool.setuptools.dynamic]
            dependencies = {file = ["requirements.txt"]}
            """)

        spec = DependencyGetterBuilder(Path("pyproject.toml")).build()
        assert isinstance(spec, PEP621DependencyGetter)


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


def test_dependency_specification_not_found_raises_exception(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    with run_within_dir(tmp_path):
        pyproject_toml_path = Path("pyproject.toml")

        with pyproject_toml_path.open("w") as f:
            f.write('[build-system]\nrequires = ["maturin>=1.5,<2.0"]\nbuild-backend = "maturin"')

    with (
        caplog.at_level(logging.DEBUG),
        run_within_dir(tmp_path),
        pytest.raises(
            DependencySpecificationNotFoundError,
            match=re.escape(
                "No file called 'pyproject.toml' with a [tool.poetry.dependencies], [tool.pdm] or [project] section or"
                " file(s) called 'req/req.txt' found. Exiting."
            ),
        ),
    ):
        DependencyGetterBuilder(Path("pyproject.toml"), requirements_files=("req/req.txt",)).build()

    assert caplog.messages == [
        "pyproject.toml found!",
        (
            "pyproject.toml does not contain a [tool.poetry] section, so Poetry is not used to specify the"
            " project's dependencies."
        ),
        (
            "pyproject.toml does not contain a [tool.uv.dev-dependencies] section, so uv is not used to specify the"
            " project's dependencies."
        ),
        (
            "pyproject.toml does not contain a [tool.pdm.dev-dependencies] section, so PDM is not used to specify the"
            " project's dependencies."
        ),
        (
            "pyproject.toml does not contain a [project] section, so PEP 621 is not used to specify the project's"
            " dependencies."
        ),
    ]


def test_check_for_requirements_in_file_with_requirements_in(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    with run_within_dir(tmp_path):
        # Setup: Create a requirements.in file in the temporary directory
        requirements_in_path = Path("requirements.in")
        requirements_in_path.touch()
        requirements_txt_path = Path("requirements.txt")
        requirements_txt_path.touch()

        # Use caplog to capture logging at the INFO level
        with caplog.at_level(logging.INFO):
            spec = DependencyGetterBuilder(
                config=Path("pyproject.toml"),
                requirements_files=("requirements.txt",),
                using_default_requirements_files=True,
            ).build()

        # Assert that requirements_files is updated correctly
        assert spec.requirements_files == ("requirements.in",)  # type: ignore[attr-defined]

        # Assert that the expected log message is present
        expected_log = (
            "Detected a 'requirements.in' file in the project and no 'requirements-files' were explicitly specified. "
            "Automatically using 'requirements.in' as the source for the project's dependencies. To specify a different source for "
            "the project's dependencies, use the '--requirements-files' option."
        )
        assert expected_log in caplog.text
