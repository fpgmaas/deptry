from deptry.dependency import Dependency
from deptry.module import Module
from deptry.obsolete_dependencies_finder import ObsoleteDependenciesFinder


def test_simple():
    dependencies = [Dependency("click"), Dependency("toml")]
    deps = ObsoleteDependenciesFinder(imported_modules=["click"], dependencies=dependencies).find()
    assert len(deps) == 1
    assert deps[0] == "toml"


def test_simple():
    dependencies = [Dependency("click"), Dependency("toml")]
    deps = ObsoleteDependenciesFinder(imported_modules=["toml"], dependencies=dependencies).find()
    assert len(deps) == 1
    assert deps[0] == "click"


def test_top_level():
    """
    Test if top-level information is read, and correctly used to not mark a dependency as obsolete.
    mpl_toolkits is in the top-level of matplotlib, so matplotlib should not be marked as an obsolete dependency.
    """
    dependencies = [Dependency("matplotlib")]
    deps = ObsoleteDependenciesFinder(imported_modules=["mpl_toolkits"], dependencies=dependencies).find()
    assert len(deps) == 0


def test_without_top_level():
    """
    Test if packages without top-level information are correctly
    """
    dependencies = [Dependency("isort")]
    deps = ObsoleteDependenciesFinder(imported_modules=["isort"], dependencies=dependencies).find()
    assert len(deps) == 0
