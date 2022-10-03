import os

import pytest

from deptry.dependency_specification_detector import (
    DependencyManagementFormat,
    DependencySpecificationDetector,
)
from deptry.utils import run_within_dir


def test_pyproject_toml(tmp_path):
    with run_within_dir(tmp_path):
        with open("pyproject.toml", "w") as f:
            f.write('[tool.poetry.dependencies]\nfake = "10"')

        spec = DependencySpecificationDetector().detect()
        assert spec == DependencyManagementFormat.POETRY


def test_requirements_txt(tmp_path):
    with run_within_dir(tmp_path):
        with open("requirements.txt", "w") as f:
            f.write('foo >= "1.0"')

        spec = DependencySpecificationDetector().detect()
        assert spec == DependencyManagementFormat.REQUIREMENTS_TXT


def test_pdm(tmp_path):
    with run_within_dir(tmp_path):
        with open("pyproject.toml", "w") as f:
            f.write('[project]\ndependencies=["foo"]\n[tool.pdm]\nversion = {source = "scm"}')

        spec = DependencySpecificationDetector().detect()
        assert spec == DependencyManagementFormat.PDM


def test_both(tmp_path):
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


def test_requirements_txt_with_argument(tmp_path):
    with run_within_dir(tmp_path):
        with open("req.txt", "w") as f:
            f.write('foo >= "1.0"')

        spec = DependencySpecificationDetector(requirements_txt=("req.txt",)).detect()
        assert spec == DependencyManagementFormat.REQUIREMENTS_TXT


def test_requirements_txt_with_argument_not_root_directory(tmp_path):
    with run_within_dir(tmp_path):
        os.mkdir("req")
        with open("req/req.txt", "w") as f:
            f.write('foo >= "1.0"')

        spec = DependencySpecificationDetector(requirements_txt=("req/req.txt",)).detect()
        assert spec == DependencyManagementFormat.REQUIREMENTS_TXT


def test_raises_filenotfound_error(tmp_path):
    with run_within_dir(tmp_path):
        with pytest.raises(FileNotFoundError) as e:
            DependencySpecificationDetector(requirements_txt=("req/req.txt",)).detect()
        assert (
            "No file called 'pyproject.toml' with a [tool.poetry.dependencies] or [tool.pdm] section or file(s)"
            in str(e)
        )
