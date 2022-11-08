from deptry.dependency import Dependency
from deptry.issues_finder.missing import MissingDependenciesFinder
from deptry.module import ModuleBuilder


def test_simple():
    dependencies = []
    modules = [ModuleBuilder("foobar", {"foo"}, dependencies).build()]

    deps = MissingDependenciesFinder(imported_modules=modules, dependencies=dependencies).find()

    assert deps == ["foobar"]


def test_local_module():
    dependencies = []
    modules = [ModuleBuilder("foobar", {"foo", "foobar"}, dependencies).build()]

    deps = MissingDependenciesFinder(imported_modules=modules, dependencies=dependencies).find()

    assert deps == []


def test_simple_with_ignore():
    dependencies = []
    modules = [ModuleBuilder("foobar", {"foo", "bar"}, dependencies).build()]

    deps = MissingDependenciesFinder(
        imported_modules=modules, dependencies=dependencies, ignored_modules=("foobar",)
    ).find()

    assert deps == []


def test_no_error():
    """
    This should run without an error, even though `foo` is not installed.
    """

    dependencies = [Dependency("foo")]
    module = ModuleBuilder("foo", {"bar"}, dependencies).build()

    deps = MissingDependenciesFinder(imported_modules=[module], dependencies=dependencies).find()

    assert deps == []
