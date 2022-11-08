from deptry.dependency import Dependency
from deptry.issues_finder.misplaced_dev import MisplacedDevDependenciesFinder
from deptry.module import Module


def test_simple():
    dependencies = [Dependency("bar")]
    modules = [Module("foo", dev_top_levels=["foo"], is_dev_dependency=True)]

    deps = MisplacedDevDependenciesFinder(imported_modules=modules, dependencies=dependencies).find()

    assert deps == ["foo"]
