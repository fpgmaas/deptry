from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from deptry.dependency import Dependency


def test_simple_dependency() -> None:
    dependency = Dependency("click", Path("pyproject.toml"))
    assert dependency.name == "click"
    assert dependency.definition_file == Path("pyproject.toml")
    assert dependency.top_levels == {"click"}


def test_create_default_top_level_if_metadata_not_found() -> None:
    dependency = Dependency("Foo-bar", Path("foo/requirements.txt"))
    assert dependency.name == "Foo-bar"
    assert dependency.definition_file == Path("foo/requirements.txt")
    assert dependency.top_levels == {"foo_bar"}


def test_get_top_levels_from_distribution() -> None:
    """
    Get the packages from distribution.
    """

    with patch("deptry.dependency.get_packages_from_distribution", return_value={"foo", "bar"}):
        dependency = Dependency("Foo-bar", Path("pyproject.toml"))

    assert dependency.name == "Foo-bar"
    assert dependency.definition_file == Path("pyproject.toml")
    assert dependency.top_levels == {"foo", "bar"}


def test_get_top_levels_from_predefined() -> None:
    """
    Verify that if there are predefined top-level module names it take precedence over other lookup methods.
    """
    with patch("deptry.dependency.get_packages_from_distribution") as mock:
        dependency = Dependency("Foo-bar", Path("pyproject.toml"), module_names=["foo"])

    assert dependency.name == "Foo-bar"
    assert dependency.definition_file == Path("pyproject.toml")
    assert dependency.top_levels == {"foo"}
    mock.assert_not_called()


def test_get_top_levels_fallback() -> None:
    """
    Use the fallback option of translating the package name.
    """

    with patch("deptry.dependency.get_packages_from_distribution", return_value=None):
        dependency = Dependency("Foo-bar", Path("pyproject.toml"))

    assert dependency.name == "Foo-bar"
    assert dependency.top_levels == {"foo_bar"}
