from __future__ import annotations

from pathlib import Path

from deptry.dependency import Dependency
from deptry.imports.location import Location
from deptry.issues_finder.misplaced_dev import MisplacedDevDependenciesFinder
from deptry.module import Module, ModuleLocations
from deptry.violations import MisplacedDevDependencyViolation


def test_simple() -> None:
    dependencies = [Dependency("bar", Path("pyproject.toml"))]

    module_foo_locations = [Location(Path("foo.py"), 1, 2), Location(Path("bar.py"), 3, 4)]
    module_foo = Module("foo", dev_top_levels=["foo"], is_provided_by_dev_dependency=True)

    modules_locations = [ModuleLocations(module_foo, module_foo_locations)]

    assert MisplacedDevDependenciesFinder(modules_locations, dependencies).find() == [
        MisplacedDevDependencyViolation(module_foo, location) for location in module_foo_locations
    ]
