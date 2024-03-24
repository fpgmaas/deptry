from __future__ import annotations

import logging
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING
from unittest import mock

import pytest

from deptry.core import Core
from deptry.dependency import Dependency
from deptry.dependency_getter.base import DependenciesExtract
from deptry.exceptions import UnsupportedPythonVersionError
from deptry.imports.location import Location
from deptry.module import Module
from deptry.stdlibs import STDLIBS_PYTHON
from deptry.violations import (
    DEP001MissingDependencyViolation,
    DEP002UnusedDependencyViolation,
    DEP003TransitiveDependencyViolation,
    DEP004MisplacedDevDependencyViolation,
)
from tests.utils import create_files, run_within_dir

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture


def test__get_sorted_violations() -> None:
    violations = [
        DEP004MisplacedDevDependencyViolation(Module("foo"), Location(Path("foo.py"), 1, 0)),
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("foo.py"), 2, 0)),
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("foo.py"), 1, 0)),
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("bar.py"), 3, 1)),
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("bar.py"), 2, 1)),
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("bar.py"), 3, 0)),
    ]

    assert Core._get_sorted_violations(violations) == [
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("bar.py"), 2, 1)),
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("bar.py"), 3, 0)),
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("bar.py"), 3, 1)),
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("foo.py"), 1, 0)),
        DEP004MisplacedDevDependencyViolation(Module("foo"), Location(Path("foo.py"), 1, 0)),
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("foo.py"), 2, 0)),
    ]


@pytest.mark.parametrize(
    ("known_first_party", "root_suffix", "expected"),
    [
        (
            (),
            "",
            {"module_with_init", "module_without_init", "local_file"},
        ),
        (
            ("module_with_init", "module_without_init"),
            "",
            {"module_with_init", "module_without_init", "local_file"},
        ),
        (
            ("module_without_init",),
            "module_with_init",
            {"foo", "module_without_init", "subdirectory"},
        ),
    ],
)
def test__get_local_modules(
    tmp_path: Path, known_first_party: tuple[str, ...], root_suffix: str, expected: set[str]
) -> None:
    with run_within_dir(tmp_path):
        create_files([
            Path("module_with_init/__init__.py"),
            Path("module_with_init/foo.py"),
            Path("module_with_init/subdirectory/__init__.py"),
            Path("module_with_init/subdirectory/foo.py"),
            Path("module_without_init/bar.py"),
            Path("local_file.py"),
        ])

        assert (
            Core(
                root=(tmp_path / root_suffix,),
                config=Path("pyproject.toml"),
                no_ansi=False,
                per_rule_ignores={},
                ignore=(),
                exclude=(),
                extend_exclude=(),
                using_default_exclude=True,
                ignore_notebooks=False,
                requirements_files=(),
                requirements_files_dev=(),
                known_first_party=known_first_party,
                json_output="",
                package_module_name_map={},
                pep621_dev_dependency_groups=(),
                using_default_requirements_files=True,
            )._get_local_modules()
            == expected
        )


@pytest.mark.skipif(sys.version_info >= (3, 10), reason="mapping is only used for Python < 3.10")
def test__get_stdlib_packages_without_stdlib_module_names() -> None:
    assert Core._get_stdlib_modules() == STDLIBS_PYTHON[f"{sys.version_info[0]}{sys.version_info[1]}"]


@pytest.mark.skipif(sys.version_info < (3, 10), reason="only Python >= 3.10 has sys.stdlib_module_names")
def test__get_stdlib_packages_with_stdlib_module_names() -> None:
    assert Core._get_stdlib_modules() == sys.stdlib_module_names  # type: ignore[attr-defined, unused-ignore]


@pytest.mark.parametrize(
    "version_info",
    [
        (sys.version_info[0], sys.version_info[1] + 1, 0),
        (sys.version_info[0], sys.version_info[1] + 1, 13),
        (sys.version_info[0] + 1, sys.version_info[1], 0),
        (sys.version_info[0], sys.version_info[1] + 1, 0, "beta", 1),
        (sys.version_info[0], sys.version_info[1] + 1, 0, "candidate", 1),
    ],
)
@pytest.mark.skipif(sys.version_info < (3, 10), reason="only Python >= 3.10 has sys.stdlib_module_names")
def test__get_stdlib_packages_with_stdlib_module_names_future_version(version_info: tuple[int | str, ...]) -> None:
    """Test that future versions of Python not yet tested on the CI will also work."""
    with mock.patch("sys.version_info", (sys.version_info[0], sys.version_info[1] + 1, 0)):
        assert Core._get_stdlib_modules() == sys.stdlib_module_names  # type: ignore[attr-defined, unused-ignore]


@pytest.mark.parametrize(
    "version_info",
    [
        (2, 1, 0),
        (2, 7, 0),
        (2, 7, 15),
        (3, 6, 0),
        (3, 6, 7),
        (3, 6, 7, "candidate", 1),
    ],
)
def test__get_stdlib_packages_unsupported(version_info: tuple[int | str, ...]) -> None:
    """It should raise an error when Python version is unsupported."""
    with mock.patch("sys.version_info", version_info), pytest.raises(
        UnsupportedPythonVersionError,
        match=re.escape(
            f"Python version {version_info[0]}.{version_info[1]} is not supported. Only versions >= 3.8 are supported."
        ),
    ):
        Core._get_stdlib_modules()


def test__exit_with_violations() -> None:
    violations = [
        DEP001MissingDependencyViolation(Module("foo"), Location(Path("foo.py"), 1, 2)),
        DEP002UnusedDependencyViolation(Dependency("foo", Path("pyproject.toml")), Location(Path("pyproject.toml"))),
        DEP003TransitiveDependencyViolation(Module("foo"), Location(Path("foo.py"), 1, 2)),
        DEP004MisplacedDevDependencyViolation(Module("foo"), Location(Path("foo.py"), 1, 2)),
    ]

    with pytest.raises(SystemExit) as e:
        Core._exit(violations)

    assert e.type == SystemExit
    assert e.value.code == 1


def test__exit_without_violations() -> None:
    with pytest.raises(SystemExit) as e:
        Core._exit([])

    assert e.type == SystemExit
    assert e.value.code == 0


@pytest.mark.parametrize(
    ("dependencies", "dev_dependencies", "expected_logs"),
    [
        (
            [],
            [],
            [],
        ),
        (
            [
                Dependency("foo", Path("pyproject.toml")),
                Dependency("bar", Path("pyproject.toml")),
            ],
            [
                Dependency("dev", Path("pyproject.toml")),
                Dependency("another-dev", Path("pyproject.toml")),
            ],
            [
                "The project contains the following dependencies:",
                "Dependency 'foo' with top-levels: {'foo'}.",
                "Dependency 'bar' with top-levels: {'bar'}.",
                "",
                "The project contains the following dev dependencies:",
                "Dependency 'dev' with top-levels: {'dev'}.",
                "Dependency 'another-dev' with top-levels: {'another_dev'}.",
                "",
            ],
        ),
    ],
)
def test__log_dependencies(
    dependencies: list[Dependency],
    dev_dependencies: list[Dependency],
    expected_logs: list[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.DEBUG):
        Core._log_dependencies(DependenciesExtract(dependencies, dev_dependencies))

    assert caplog.messages == expected_logs


def test_check_for_requirements_in_file_with_requirements_in(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    with run_within_dir(tmp_path):
        # Setup: Create a requirements.in file in the temporary directory
        requirements_in_path = Path("requirements.in")
        requirements_in_path.touch()
        requirements_txt_path = Path("requirements.txt")
        requirements_txt_path.touch()

        # Initialize Core object with the temporary path as the root, and simulate the default usage of requirements files
        core_instance = Core(
            root=(tmp_path,),
            config=Path("pyproject.toml"),
            no_ansi=False,
            per_rule_ignores={},
            ignore=(),
            exclude=(),
            extend_exclude=(),
            using_default_exclude=True,
            ignore_notebooks=False,
            requirements_files=(),
            using_default_requirements_files=True,  # Important for this test
            requirements_files_dev=(),
            known_first_party=(),
            json_output="",
            package_module_name_map={},
            pep621_dev_dependency_groups=(),
        )

        # Use caplog to capture logging at the INFO level
        with caplog.at_level(logging.INFO):
            core_instance._check_for_requirements_in_file()

        # Assert that requirements_files is updated correctly
        assert core_instance.requirements_files == ("requirements.in",)

        # Assert that the expected log message is present
        expected_log = (
            "Detected a 'requirements.in' file in the project and no 'requirements-files' were explicitly specified. "
            "Automatically using 'requirements.in' as the source for the project's dependencies. To specify a different source for "
            "the project's dependencies, use the '--requirements-files' option."
        )
        assert expected_log in caplog.text
