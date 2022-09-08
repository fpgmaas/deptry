from deptry.dependency import Dependency
from deptry.issue_finders.transitive import TransitiveDependenciesFinder
from deptry.module import Module


def test_simple():
    """
    matplotlib is in testing environment which requires pillow, so pillow should be found as transitive.
    """
    dependencies = []
    modules = [Module("pillow", dependencies)]
    deps = TransitiveDependenciesFinder(imported_modules=modules, dependencies=dependencies).find()
    assert len(deps) == 1
    assert deps[0] == "Pillow"


def test_simple_with_ignore():
    dependencies = []
    modules = [Module("foobar", dependencies)]
    deps = TransitiveDependenciesFinder(
        imported_modules=modules, dependencies=dependencies, list_to_ignore=["foobar"]
    ).find()
    assert len(deps) == 0
