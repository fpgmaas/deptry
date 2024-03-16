from __future__ import annotations

from enum import Enum

DEPTRY_WHEEL_DIRECTORY = "build/functional_tests/deptry"


class Project(str, Enum):
    EXAMPLE = "example_project"
    PEP_621 = "pep_621_project"
    FUTURE_DEPRECATED_OBSOLETE_ARGUMENT = "project_with_future_deprecated_obsolete_argument"
    GITIGNORE = "project_with_gitignore"
    MULTIPLE_SOURCE_DIRECTORIES = "project_with_multiple_source_directories"
    PDM = "project_with_pdm"
    POETRY = "project_with_poetry"
    PYPROJECT_DIFFERENT_DIRECTORY = "project_with_pyproject_different_directory"
    REQUIREMENTS_TXT = "project_with_requirements_txt"
    SRC_DIRECTORY = "project_with_src_directory"

    def __str__(self) -> str:
        return self.value
