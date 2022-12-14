from __future__ import annotations

from deptry.dependency import Dependency
from deptry.issues_finder.transitive import TransitiveDependenciesFinder
from deptry.module import ModuleBuilder


def test_simple() -> None:
    """
    black is in testing environment which requires platformdirs, so platformdirs should be found as transitive.
    """
    dependencies: list[Dependency] = []
    modules = [ModuleBuilder("platformdirs", {"foo"}, dependencies).build()]

    deps = TransitiveDependenciesFinder(imported_modules=modules, dependencies=dependencies).find()

    assert deps == ["platformdirs"]


def test_simple_with_ignore() -> None:
    dependencies: list[Dependency] = []
    modules = [ModuleBuilder("foobar", {"foo"}, dependencies).build()]

    deps = TransitiveDependenciesFinder(
        imported_modules=modules, dependencies=dependencies, ignored_modules=("foobar",)
    ).find()

    assert deps == []
