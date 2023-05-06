from __future__ import annotations

from pathlib import Path

from deptry.dependency import Dependency
from deptry.imports.location import Location
from deptry.issues_finder.obsolete import ObsoleteDependenciesFinder
from deptry.module import ModuleBuilder, ModuleLocations
from deptry.violations import ObsoleteDependencyViolation


def test_simple() -> None:
    dependency_toml = Dependency("toml", Path("pyproject.toml"))
    dependencies = [Dependency("click", Path("pyproject.toml")), dependency_toml]
    modules_locations = [
        ModuleLocations(
            ModuleBuilder("click", {"foo"}, frozenset(), dependencies).build(), [Location(Path("foo.py"), 1, 2)]
        )
    ]

    assert ObsoleteDependenciesFinder(modules_locations, dependencies).find() == [
        ObsoleteDependencyViolation(dependency_toml, Location(Path("pyproject.toml")))
    ]


def test_simple_with_ignore() -> None:
    dependencies = [Dependency("click", Path("pyproject.toml")), Dependency("toml", Path("pyproject.toml"))]
    modules_locations = [
        ModuleLocations(
            ModuleBuilder("toml", {"foo"}, frozenset(), dependencies).build(), [Location(Path("foo.py"), 1, 2)]
        )
    ]

    assert ObsoleteDependenciesFinder(modules_locations, dependencies, ignored_modules=("click",)).find() == []


def test_top_level() -> None:
    """
    Test if top-level information is read, and correctly used to not mark a dependency as obsolete.
    blackd is in the top-level of black, so black should not be marked as an obsolete dependency.
    """
    dependencies = [Dependency("black", Path("pyproject.toml"))]
    modules_locations = [
        ModuleLocations(
            ModuleBuilder("blackd", {"foo"}, frozenset(), dependencies).build(), [Location(Path("foo.py"), 1, 2)]
        )
    ]

    deps = ObsoleteDependenciesFinder(modules_locations, dependencies).find()

    assert deps == []


def test_without_top_level() -> None:
    """
    Test if packages without top-level information are correctly maked as obsolete
    """
    dependencies = [Dependency("isort", Path("pyproject.toml"))]
    modules_locations = [
        ModuleLocations(
            ModuleBuilder("isort", {"foo"}, frozenset(), dependencies).build(), [Location(Path("foo.py"), 1, 2)]
        )
    ]

    assert ObsoleteDependenciesFinder(modules_locations, dependencies).find() == []
