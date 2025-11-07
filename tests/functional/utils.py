from __future__ import annotations

from enum import Enum

DEPTRY_WHEEL_DIRECTORY = "build/functional_tests/deptry"


class Project(str, Enum):
    EXAMPLE = "example"
    PEP_621 = "pep_621"
    GITIGNORE = "gitignore"
    MULTIPLE_SOURCE_DIRECTORIES = "multiple_source_directories"
    NAMESPACE = "namespace"
    PDM = "pdm"
    POETRY = "poetry"
    POETRY_PEP_621 = "poetry_pep_621"
    PYPROJECT_DIFFERENT_DIRECTORY = "pyproject_different_directory"
    REQUIREMENTS_TXT = "requirements_txt"
    REQUIREMENTS_IN = "requirements_in"
    SETUPTOOLS_DYNAMIC_DEPENDENCIES = "setuptools_dynamic_dependencies"
    SRC_DIRECTORY = "src_directory"
    UV = "uv"

    def __str__(self) -> str:
        return self.value
