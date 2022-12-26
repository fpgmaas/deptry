import os
from pathlib import Path

import pytest

from deptry.dependency_specification_detector import DependencyManagementFormat, DependencySpecificationDetector
from tests.utils import run_within_dir


def test_poetry(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        with open("pyproject.toml", "w") as f:
            f.write('[tool.poetry.dependencies]\nfake = "10"')

        spec = DependencySpecificationDetector().detect()
        assert spec == DependencyManagementFormat.POETRY


def test_requirements_txt(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        with open("requirements.txt", "w") as f:
            f.write('foo >= "1.0"')

        spec = DependencySpecificationDetector().detect()
        assert spec == DependencyManagementFormat.REQUIREMENTS_TXT


def test_pdm_with_dev_dependencies(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        with open("pyproject.toml", "w") as f:
            f.write(
                '[project]\ndependencies=["foo"]\n[tool.pdm]\nversion = {source ='
                ' "scm"}\n[tool.pdm.dev-dependencies]\ngroup=["bar"]'
            )

        spec = DependencySpecificationDetector().detect()
        assert spec == DependencyManagementFormat.PDM


def test_pdm_without_dev_dependencies(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        with open("pyproject.toml", "w") as f:
            f.write('[project]\ndependencies=["foo"]\n[tool.pdm]\nversion = {source = "scm"}')

        spec = DependencySpecificationDetector().detect()
        assert spec == DependencyManagementFormat.PEP_621


def test_pep_621(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        with open("pyproject.toml", "w") as f:
            f.write('[project]\ndependencies=["foo"]')

        spec = DependencySpecificationDetector().detect()
        assert spec == DependencyManagementFormat.PEP_621


def test_both(tmp_path: Path) -> None:
    """
    If both are found, result should be 'poetry'
    """

    with run_within_dir(tmp_path):
        with open("pyproject.toml", "w") as f:
            f.write('[tool.poetry.dependencies]\nfake = "10"')

        with open("requirements.txt", "w") as f:
            f.write('foo >= "1.0"')

        spec = DependencySpecificationDetector().detect()
        assert spec == DependencyManagementFormat.POETRY


def test_requirements_txt_with_argument(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        with open("req.txt", "w") as f:
            f.write('foo >= "1.0"')

        spec = DependencySpecificationDetector(requirements_txt=("req.txt",)).detect()
        assert spec == DependencyManagementFormat.REQUIREMENTS_TXT


def test_requirements_txt_with_argument_not_root_directory(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        os.mkdir("req")
        with open("req/req.txt", "w") as f:
            f.write('foo >= "1.0"')

        spec = DependencySpecificationDetector(requirements_txt=("req/req.txt",)).detect()
        assert spec == DependencyManagementFormat.REQUIREMENTS_TXT


def test_raises_filenotfound_error(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        with pytest.raises(FileNotFoundError) as e:
            DependencySpecificationDetector(requirements_txt=("req/req.txt",)).detect()
        assert (
            "No file called 'pyproject.toml' with a [tool.poetry.dependencies], [tool.pdm] or [project] section or"
            " file(s)"
            in str(e)
        )
