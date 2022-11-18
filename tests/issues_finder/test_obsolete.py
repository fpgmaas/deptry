from deptry.dependency import Dependency
from deptry.issues_finder.obsolete import ObsoleteDependenciesFinder
from deptry.module import ModuleBuilder


def test_simple() -> None:
    dependencies = [Dependency("click"), Dependency("toml")]
    modules = [ModuleBuilder("click", {"foo"}, dependencies).build()]

    deps = ObsoleteDependenciesFinder(imported_modules=modules, dependencies=dependencies).find()

    assert deps == ["toml"]


def test_simple_with_ignore() -> None:
    dependencies = [Dependency("click"), Dependency("toml")]
    modules = [ModuleBuilder("toml", {"foo"}, dependencies).build()]

    deps = ObsoleteDependenciesFinder(
        imported_modules=modules, dependencies=dependencies, ignored_modules=("click",)
    ).find()

    assert deps == []


def test_top_level() -> None:
    """
    Test if top-level information is read, and correctly used to not mark a dependency as obsolete.
    blackd is in the top-level of black, so black should not be marked as an obsolete dependency.
    """
    dependencies = [Dependency("black")]
    modules = [ModuleBuilder("blackd", {"foo"}, dependencies).build()]

    deps = ObsoleteDependenciesFinder(imported_modules=modules, dependencies=dependencies).find()

    assert deps == []


def test_without_top_level() -> None:
    """
    Test if packages without top-level information are correctly maked as obsolete
    """
    dependencies = [Dependency("isort")]
    modules = [ModuleBuilder("isort", {"foo"}, dependencies).build()]

    deps = ObsoleteDependenciesFinder(imported_modules=modules, dependencies=dependencies).find()

    assert deps == []
