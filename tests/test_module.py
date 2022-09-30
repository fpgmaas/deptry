from deptry.dependency import Dependency
from deptry.module import ModuleBuilder


def test_simple_import():
    module = ModuleBuilder("click").build()
    assert module.package == "click"


def test_top_level():
    # Test if no error is raised, argument is accepted.
    dependency = Dependency("beautifulsoup4")
    dependency.top_levels = ["bs4"]
    module = ModuleBuilder("bs4", [dependency]).build()
    assert module.package is None


def test_stdlib():
    module = ModuleBuilder("sys").build()
    assert module.package is None
    assert module.standard_library
