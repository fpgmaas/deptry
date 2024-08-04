from __future__ import annotations

from pathlib import Path

from deptry.dependency import Dependency
from deptry.imports.location import Location
from deptry.module import Module, ModuleLocations
from deptry.violations import DEP004MisplacedDevDependencyViolation
from deptry.violations.dep004_misplaced_dev.finder import DEP004MisplacedDevDependenciesFinder


def test_simple() -> None:
    dependencies = [Dependency("bar", Path("pyproject.toml"))]

    module_foo_locations = [Location(Path("foo.py"), 1, 2), Location(Path("bar.py"), 3, 4)]
    module_foo = Module("foo", dev_top_levels=["foo"], is_provided_by_dev_dependency=True)

    modules_locations = [ModuleLocations(module_foo, module_foo_locations)]

    assert DEP004MisplacedDevDependenciesFinder(modules_locations, dependencies, frozenset()).find() == [
        DEP004MisplacedDevDependencyViolation(module_foo, location) for location in module_foo_locations
    ]


def test_regular_and_dev_dependency() -> None:
    """
    If a dependency is both a regular and a development dependency, no 'misplaced dev dependency' violation
    should be detected if it is used in the code base.
    """

    dependencies = [Dependency("foo", Path("pyproject.toml"))]

    module_foo_locations = [Location(Path("foo.py"), 1, 2)]
    module_foo = Module(
        "foo", dev_top_levels=["foo"], is_provided_by_dev_dependency=True, is_provided_by_dependency=True
    )

    modules_locations = [ModuleLocations(module_foo, module_foo_locations)]

    assert not DEP004MisplacedDevDependenciesFinder(modules_locations, dependencies, frozenset()).find()
