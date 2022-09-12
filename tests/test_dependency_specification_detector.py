import os
from distutils.command.config import config

from deptry.config import Config
from deptry.dependency_specification_detector import DependencySpecificationDetector
from deptry.utils import run_within_dir


def test_pyproject_toml(tmp_path):
    with run_within_dir(tmp_path):
        with open("pyproject.toml", "w") as f:
            f.write('[tool.poetry.dependencies]\nfake = "10"')

        spec = DependencySpecificationDetector().detect()
        assert spec == "pyproject_toml"


def test_requirements_txt(tmp_path):
    with run_within_dir(tmp_path):
        with open("requirements.txt", "w") as f:
            f.write('foo >= "1.0"')

        spec = DependencySpecificationDetector().detect()
        assert spec == "requirements_txt"


def test_both(tmp_path):
    """
    If both are found, result should be 'pyproject_toml'
    """

    with run_within_dir(tmp_path):

        with open("pyproject.toml", "w") as f:
            f.write('[tool.poetry.dependencies]\nfake = "10"')

        with open("requirements.txt", "w") as f:
            f.write('foo >= "1.0"')

        spec = DependencySpecificationDetector().detect()
        assert spec == "pyproject_toml"


def test_requirements_txt_with_argument(tmp_path):
    with run_within_dir(tmp_path):
        with open("req.txt", "w") as f:
            f.write('foo >= "1.0"')

        spec = DependencySpecificationDetector(requirements_txt="req.txt").detect()
        assert spec == "requirements_txt"


def test_requirements_txt_with_argument(tmp_path):
    with run_within_dir(tmp_path):
        os.mkdir("req")
        with open("req/req.txt", "w") as f:
            f.write('foo >= "1.0"')

        spec = DependencySpecificationDetector(requirements_txt="req/req.txt").detect()
        assert spec == "requirements_txt"
