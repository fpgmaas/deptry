from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from deptry.imports.location import Location
from deptry.module import ModuleBuilder, ModuleLocations
from deptry.violations import DEP003TransitiveDependenciesFinder
from deptry.violations.dep003_transitive.violation import DEP003TransitiveDependencyViolation

if TYPE_CHECKING:
    from deptry.dependency import Dependency


def test_simple() -> None:
    """
    black is in testing environment which requires platformdirs, so platformdirs should be found as transitive.
    """
    dependencies: list[Dependency] = []

    module_platformdirs_locations = [Location(Path("foo.py"), 1, 2), Location(Path("bar.py"), 3, 4)]
    module_platformdirs = ModuleBuilder("platformdirs", {"foo"}, frozenset(), dependencies).build()

    modules_locations = [ModuleLocations(module_platformdirs, module_platformdirs_locations)]

    assert DEP003TransitiveDependenciesFinder(modules_locations, dependencies).find() == [
        DEP003TransitiveDependencyViolation(module_platformdirs, location) for location in module_platformdirs_locations
    ]


def test_simple_with_ignore() -> None:
    dependencies: list[Dependency] = []
    modules_locations = [
        ModuleLocations(
            ModuleBuilder("foobar", {"foo"}, frozenset(), dependencies).build(), [Location(Path("foo.py"), 1, 2)]
        )
    ]

    assert DEP003TransitiveDependenciesFinder(modules_locations, dependencies, ignored_modules=("foobar",)).find() == []
