from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from pathlib import Path
from unittest.mock import patch

import pytest

from deptry.dependency import Dependency
from deptry.module import ModuleBuilder


def test_simple_import() -> None:
    module = ModuleBuilder("click", {"foo", "bar"}, frozenset()).build()
    assert module.package == "click"
    assert module.standard_library is False
    assert module.local_module is False


def test_top_level() -> None:
    # Test if no error is raised, argument is accepted.
    dependency = Dependency("beautifulsoup4", Path("pyproject.toml"))
    dependency.top_levels = {"bs4"}
    module = ModuleBuilder("bs4", {"foo", "bar"}, frozenset(), [dependency]).build()
    assert module.package is None
    assert module.standard_library is False
    assert module.local_module is False


def test_stdlib() -> None:
    module = ModuleBuilder("sys", {"foo", "bar"}, frozenset({"sys"})).build()
    assert module.package is None
    assert module.standard_library is True
    assert module.local_module is False


def test_local_module() -> None:
    module = ModuleBuilder("click", {"foo", "click"}, frozenset()).build()
    assert module.package is None
    assert module.standard_library is False
    assert module.local_module is True


def test_transitive_module() -> None:
    with (
        patch("deptry.module.metadata", side_effect=PackageNotFoundError),
        patch("deptry.module.find_spec", return_value="bar"),
    ):
        module = ModuleBuilder("foo", set(), frozenset()).build()

    assert module.package == "foo"
    assert module.standard_library is False
    assert module.local_module is False


def test_transitive_module_no_spec() -> None:
    with (
        patch("deptry.module.metadata", side_effect=PackageNotFoundError),
        patch("deptry.module.find_spec", return_value=None),
    ):
        module = ModuleBuilder("foo", set(), frozenset()).build()

    assert module.package is None
    assert module.standard_library is False
    assert module.local_module is False


@pytest.mark.parametrize("exception", [ModuleNotFoundError, ValueError])
def test_transitive_module_spec_error(exception: Exception) -> None:
    with (
        patch("deptry.module.metadata", side_effect=PackageNotFoundError),
        patch("deptry.module.find_spec", side_effect=exception),
    ):
        module = ModuleBuilder("foo", set(), frozenset()).build()

    assert module.package is None
    assert module.standard_library is False
    assert module.local_module is False
