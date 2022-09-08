from deptry.dependency import Dependency
from deptry.issue_finders.missing import MissingDependenciesFinder
from deptry.module import ModuleBuilder


def test_simple():
    dependencies = []
    modules = [ModuleBuilder("foobar", dependencies).build()]
    deps = MissingDependenciesFinder(imported_modules=modules, dependencies=dependencies).find()
    assert len(deps) == 1
    assert deps[0] == "foobar"


def test_simple_with_ignore():
    dependencies = []
    modules = [ModuleBuilder("foobar", dependencies).build()]
    deps = MissingDependenciesFinder(
        imported_modules=modules, dependencies=dependencies, ignore_missing=["foobar"]
    ).find()
    assert len(deps) == 0
