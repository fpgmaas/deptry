from __future__ import annotations

from enum import Enum

DEPTRY_WHEEL_DIRECTORY = "build/functional_tests/deptry"


class Project(str, Enum):
    EXAMPLE = "example_project"
    PEP_621 = "pep_621_project"
    GITIGNORE = "project_with_gitignore"
    MULTIPLE_SOURCE_DIRECTORIES = "project_with_multiple_source_directories"
    NAMESPACE = "project_using_namespace"
    PDM = "project_with_pdm"
    POETRY = "project_with_poetry"
    POETRY_PEP_621 = "project_with_poetry_pep_621"
    PYPROJECT_DIFFERENT_DIRECTORY = "project_with_pyproject_different_directory"
    REQUIREMENTS_TXT = "project_with_requirements_txt"
    REQUIREMENTS_IN = "project_with_requirements_in"
    SETUPTOOLS_DYNAMIC_DEPENDENCIES = "project_with_setuptools_dynamic_dependencies"
    SRC_DIRECTORY = "project_with_src_directory"
    UV = "project_with_uv"

    def __str__(self) -> str:
        return self.value
