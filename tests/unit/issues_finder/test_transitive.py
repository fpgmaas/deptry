from __future__ import annotations

from typing import TYPE_CHECKING

from deptry.issues_finder.transitive import TransitiveDependenciesFinder
from deptry.module import ModuleBuilder
from deptry.violations import TransitiveDependencyViolation

if TYPE_CHECKING:
    from deptry.dependency import Dependency


def test_simple() -> None:
    """
    black is in testing environment which requires platformdirs, so platformdirs should be found as transitive.
    """
    dependencies: list[Dependency] = []
    module_platformdirs = ModuleBuilder("platformdirs", {"foo"}, frozenset(), dependencies).build()
    modules = [module_platformdirs]

    deps = TransitiveDependenciesFinder(imported_modules=modules, dependencies=dependencies).find()

    assert deps == [TransitiveDependencyViolation(module_platformdirs)]


def test_simple_with_ignore() -> None:
    dependencies: list[Dependency] = []
    modules = [ModuleBuilder("foobar", {"foo"}, frozenset(), dependencies).build()]

    deps = TransitiveDependenciesFinder(
        imported_modules=modules, dependencies=dependencies, ignored_modules=("foobar",)
    ).find()

    assert deps == []
