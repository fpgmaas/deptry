from __future__ import annotations

from pathlib import Path

from deptry.dependency import Dependency
from deptry.issues_finder.missing import MissingDependenciesFinder
from deptry.module import ModuleBuilder


def test_simple() -> None:
    dependencies: list[Dependency] = []
    modules = [ModuleBuilder("foobar", {"foo"}, frozenset(), dependencies).build()]

    deps = MissingDependenciesFinder(imported_modules=modules, dependencies=dependencies).find()

    assert deps == ["foobar"]


def test_local_module() -> None:
    dependencies: list[Dependency] = []
    modules = [ModuleBuilder("foobar", {"foo", "foobar"}, frozenset(), dependencies).build()]

    deps = MissingDependenciesFinder(imported_modules=modules, dependencies=dependencies).find()

    assert deps == []


def test_simple_with_ignore() -> None:
    dependencies: list[Dependency] = []
    modules = [ModuleBuilder("foobar", {"foo", "bar"}, frozenset(), dependencies).build()]

    deps = MissingDependenciesFinder(
        imported_modules=modules, dependencies=dependencies, ignored_modules=("foobar",)
    ).find()

    assert deps == []


def test_no_error() -> None:
    """
    This should run without an error, even though `foo` is not installed.
    """

    dependencies = [Dependency("foo", Path("pyproject.toml"))]
    module = ModuleBuilder("foo", {"bar"}, frozenset(), dependencies).build()

    deps = MissingDependenciesFinder(imported_modules=[module], dependencies=dependencies).find()

    assert deps == []
