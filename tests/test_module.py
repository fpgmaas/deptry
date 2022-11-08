from unittest import mock

import pytest

from deptry.dependency import Dependency
from deptry.module import ModuleBuilder


def test_simple_import():
    module = ModuleBuilder("click", {"foo", "bar"}).build()
    assert module.package == "click"
    assert module.standard_library is False
    assert module.local_module is False


def test_top_level():
    # Test if no error is raised, argument is accepted.
    dependency = Dependency("beautifulsoup4")
    dependency.top_levels = ["bs4"]
    module = ModuleBuilder("bs4", {"foo", "bar"}, [dependency]).build()
    assert module.package is None
    assert module.standard_library is False
    assert module.local_module is False


def test_stdlib():
    module = ModuleBuilder("sys", {"foo", "bar"}).build()
    assert module.package is None
    assert module.standard_library is True
    assert module.local_module is False


def test_local_module():
    module = ModuleBuilder("click", {"foo", "click"}).build()
    assert module.package is None
    assert module.standard_library is False
    assert module.local_module is True


@pytest.mark.parametrize(
    "version_info",
    [
        (3, 7, 0),
        (3, 7, 13),
        (3, 8, 4),
        (3, 9, 3),
        (3, 10, 2),
        (3, 11, 0),
        (3, 11, 1),
        (3, 11, 0, "beta", 1),
        (3, 11, 0, "candidate", 1),
    ],
)
def test__get_stdlib_packages_supported(version_info):
    """It should not raise any error when Python version is supported."""
    with mock.patch("sys.version_info", version_info):
        assert isinstance(ModuleBuilder("", set())._get_stdlib_packages(), set)


@pytest.mark.parametrize(
    "version_info",
    [
        (2, 1, 0),
        (2, 7, 0),
        (2, 7, 15),
        (3, 6, 0),
        (3, 6, 7),
        (3, 12, 0),
        (3, 12, 0, "candidate", 1),
        (4, 0, 0),
    ],
)
def test__get_stdlib_packages_unsupported(version_info):
    """It should raise an error when Python version is unsupported."""
    with mock.patch("sys.version_info", version_info), pytest.raises(ValueError):
        assert ModuleBuilder("", set())._get_stdlib_packages()
