from deptry.dependency import Dependency
from deptry.issues_finder.obsolete import ObsoleteDependenciesFinder
from deptry.module import ModuleBuilder


def test_simple():
    dependencies = [Dependency("click"), Dependency("toml")]
    modules = [ModuleBuilder("click", dependencies).build()]
    deps = ObsoleteDependenciesFinder(imported_modules=modules, dependencies=dependencies).find()
    assert len(deps) == 1
    assert deps[0] == "toml"


def test_simple_with_ignore():
    dependencies = [Dependency("click"), Dependency("toml")]
    modules = [ModuleBuilder("toml", dependencies).build()]
    deps = ObsoleteDependenciesFinder(
        imported_modules=modules, dependencies=dependencies, ignored_modules=("click",)
    ).find()
    assert len(deps) == 0


def test_top_level():
    """
    Test if top-level information is read, and correctly used to not mark a dependency as obsolete.
    blackd is in the top-level of black, so black should not be marked as an obsolete dependency.
    """
    dependencies = [Dependency("black")]
    modules = [ModuleBuilder("blackd", dependencies).build()]
    deps = ObsoleteDependenciesFinder(imported_modules=modules, dependencies=dependencies).find()
    assert len(deps) == 0


def test_without_top_level():
    """
    Test if packages without top-level information are correctly maked as obsolete
    """
    dependencies = [Dependency("isort")]
    modules = [ModuleBuilder("isort", dependencies).build()]
    deps = ObsoleteDependenciesFinder(imported_modules=modules, dependencies=dependencies).find()
    assert len(deps) == 0
