from __future__ import annotations

from pathlib import Path

from deptry.dependency import Dependency
from deptry.issues_finder.misplaced_dev import MisplacedDevDependenciesFinder
from deptry.module import Module
from deptry.violation import Violation


def test_simple() -> None:
    dependencies = [Dependency("bar", Path("pyproject.toml"))]
    module_foo = Module("foo", dev_top_levels=["foo"], is_dev_dependency=True)
    modules = [module_foo]

    deps = MisplacedDevDependenciesFinder(imported_modules=modules, dependencies=dependencies).find()

    assert deps == [Violation(MisplacedDevDependenciesFinder, module_foo)]
