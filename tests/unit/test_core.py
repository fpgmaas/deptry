from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING
from unittest import mock

import pytest

from deptry.core import Core
from deptry.dependency import Dependency
from deptry.exceptions import UnsupportedPythonVersionError
from deptry.module import Module
from deptry.stdlibs import STDLIBS_PYTHON
from deptry.violations import (
    MisplacedDevDependencyViolation,
    MissingDependencyViolation,
    ObsoleteDependencyViolation,
    TransitiveDependencyViolation,
)
from tests.utils import create_files, run_within_dir

if TYPE_CHECKING:
    from deptry.violations import Violation


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
        create_files(
            [
                Path("module_with_init/__init__.py"),
                Path("module_with_init/foo.py"),
                Path("module_with_init/subdirectory/__init__.py"),
                Path("module_with_init/subdirectory/foo.py"),
                Path("module_without_init/bar.py"),
                Path("local_file.py"),
            ]
        )

        assert (
            Core(
                root=tmp_path / root_suffix,
                config=Path("pyproject.toml"),
                ignore_obsolete=(),
                ignore_missing=(),
                ignore_transitive=(),
                ignore_misplaced_dev=(),
                skip_obsolete=False,
                skip_missing=False,
                skip_transitive=False,
                skip_misplaced_dev=False,
                exclude=(),
                extend_exclude=(),
                using_default_exclude=True,
                ignore_notebooks=False,
                requirements_txt=(),
                requirements_txt_dev=(),
                known_first_party=known_first_party,
                json_output="",
                package_module_name_map={},
            )._get_local_modules()
            == expected
        )


@pytest.mark.skipif(sys.version_info >= (3, 10), reason="mapping is only used for Python < 3.10")
def test__get_stdlib_packages_without_stdlib_module_names() -> None:
    assert Core._get_stdlib_modules() == STDLIBS_PYTHON[f"{sys.version_info[0]}{sys.version_info[1]}"]


@pytest.mark.skipif(sys.version_info < (3, 10), reason="only Python >= 3.10 has sys.stdlib_module_names")
def test__get_stdlib_packages_with_stdlib_module_names() -> None:
    assert Core._get_stdlib_modules() == sys.stdlib_module_names  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    "version_info",
    [
        (sys.version_info[0], sys.version_info[1] + 1, 0),
        (sys.version_info[0], sys.version_info[1] + 1, 13),
        (sys.version_info[0] + 1, sys.version_info[1], 0),
        (sys.version_info[0], sys.version_info[1] + 1, 0),
        (sys.version_info[0], sys.version_info[1] + 1, 0, "beta", 1),
        (sys.version_info[0], sys.version_info[1] + 1, 0, "candidate", 1),
    ],
)
@pytest.mark.skipif(sys.version_info < (3, 10), reason="only Python >= 3.10 has sys.stdlib_module_names")
def test__get_stdlib_packages_with_stdlib_module_names_future_version(version_info: tuple[int | str, ...]) -> None:
    """Test that future versions of Python not yet tested on the CI will also work."""
    with mock.patch("sys.version_info", (sys.version_info[0], sys.version_info[1] + 1, 0)):
        assert Core._get_stdlib_modules() == sys.stdlib_module_names  # type: ignore[attr-defined]


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
    violations: dict[str, list[Violation]] = {
        "missing": [MissingDependencyViolation(Module("foo"))],
        "obsolete": [ObsoleteDependencyViolation(Dependency("foo", Path("pyproject.toml")))],
        "transitive": [TransitiveDependencyViolation(Module("foo"))],
        "misplaced_dev": [MisplacedDevDependencyViolation(Module("foo"))],
    }
    with pytest.raises(SystemExit) as e:
        Core._exit(violations)

    assert e.type == SystemExit
    assert e.value.code == 1


def test__exit_without_violations() -> None:
    violations: dict[str, list[Violation]] = {}
    with pytest.raises(SystemExit) as e:
        Core._exit(violations)

    assert e.type == SystemExit
    assert e.value.code == 0
