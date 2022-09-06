from deptry.dependency import Dependency
from deptry.module import Module


def test_simple_import():
    module = Module("click")
    assert module.package == "click"


def test_top_level():
    # Test if no error is raised, argument is accepted.
    dependency = Dependency("beautifulsoup4")
    dependency.top_levels = ["bs4"]
    module = Module("bs4", [dependency])
    assert module.package == None


def test_stdlib():
    module = Module("sys")
    assert module.package is None
    assert module.standard_library
