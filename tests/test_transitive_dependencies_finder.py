from deptry.dependency import Dependency
from deptry.issue_finders.transitive import TransitiveDependenciesFinder
from deptry.module import ModuleBuilder


def test_simple():
    """
    matplotlib is in testing environment which requires pillow, so pillow should be found as transitive.
    """
    dependencies = []
    modules = [ModuleBuilder("pillow", dependencies).build()]
    deps = TransitiveDependenciesFinder(imported_modules=modules, dependencies=dependencies).find()
    assert len(deps) == 1
    assert deps[0] == "Pillow"


def test_simple_with_ignore():
    dependencies = []
    modules = [ModuleBuilder("foobar", dependencies).build()]
    deps = TransitiveDependenciesFinder(
        imported_modules=modules, dependencies=dependencies, ignore_transitive=["foobar"]
    ).find()
    assert len(deps) == 0
