from deptry.dependency import Dependency


def test_simple_dependency():
    dependency = Dependency("click")
    assert dependency.name == "click"
    assert dependency.top_levels == ["click"]
