from deptry.dependency import Dependency


def test_simple_dependency():
    dependency = Dependency("click")
    assert dependency.name == "click"
    assert dependency.top_levels == set(["click"])


def test_create_default_top_level_if_metadata_not_found():
    dependency = Dependency("Foo-bar")
    assert dependency.name == "Foo-bar"
    assert dependency.top_levels == set(["foo_bar"])
