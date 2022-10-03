from deptry.dependency import Dependency
from deptry.issues_finder.missing import MissingDependenciesFinder
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
        imported_modules=modules, dependencies=dependencies, ignored_modules=("foobar",)
    ).find()
    assert len(deps) == 0


def test_no_error():
    """
    This should run without an error, even though `foo` is not installed.
    """

    dep = Dependency("foo")
    module = ModuleBuilder("foo", [dep]).build()

    deps = MissingDependenciesFinder(imported_modules=[module], dependencies=[dep]).find()
    assert len(deps) == 0
