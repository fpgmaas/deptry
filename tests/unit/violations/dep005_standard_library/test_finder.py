from __future__ import annotations

from pathlib import Path

from deptry.dependency import Dependency
from deptry.imports.location import Location
from deptry.module import ModuleBuilder, ModuleLocations
from deptry.violations import DEP005StandardLibraryDependencyFinder, DEP005StandardLibraryDependencyViolation


def test_simple() -> None:
    dependency_asyncio = Dependency("asyncio", Path("pyproject.toml"))
    dependencies = [dependency_asyncio]
    modules_locations = [
        ModuleLocations(
            ModuleBuilder("asyncio", {"foo"}, frozenset(), dependencies).build(), [Location(Path("foo.py"), 1, 2)]
        )
    ]

    assert DEP005StandardLibraryDependencyFinder(
        imported_modules_with_locations=modules_locations, dependencies=dependencies, stdlib_modules={"asyncio"}
    ).find() == [DEP005StandardLibraryDependencyViolation(dependency_asyncio, Location(Path("pyproject.toml")))]


def test_simple_with_ignore() -> None:
    dependency_asyncio = Dependency("asyncio", Path("pyproject.toml"))
    dependencies = [dependency_asyncio]
    modules_locations = [
        ModuleLocations(
            ModuleBuilder("asyncio", {"foo"}, frozenset(), dependencies).build(), [Location(Path("foo.py"), 1, 2)]
        )
    ]

    assert (
        DEP005StandardLibraryDependencyFinder(
            imported_modules_with_locations=modules_locations,
            dependencies=dependencies,
            stdlib_modules={"asyncio"},
            ignored_modules=("asyncio",),
        ).find()
        == []
    )
