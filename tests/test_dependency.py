from unittest.mock import patch

from deptry.dependency import Dependency


def test_simple_dependency():
    dependency = Dependency("click")
    assert dependency.name == "click"
    assert dependency.top_levels == set(["click"])


def test_create_default_top_level_if_metadata_not_found():
    dependency = Dependency("Foo-bar")
    assert dependency.name == "Foo-bar"
    assert dependency.top_levels == set(["foo_bar"])


def test_read_top_level_from_top_level_txt():
    """
    Read the top-levels.txt file
    """

    class MockDistribution:
        def __init__(self):
            pass

        def read_text(self, file_name):
            return "foo\nbar"

    with patch("deptry.dependency.metadata.distribution") as mock:
        mock.return_value = MockDistribution()
        dependency = Dependency("Foo-bar")
        assert dependency.name == "Foo-bar"
        assert dependency.top_levels == set(["foo_bar", "foo", "bar"])


def test_read_top_level_from_record():
    """
    Verify that if top-level.txt not found, an attempt is made to extract top-level module names from
    the metadata RECORD file.
    """

    class MockDistribution:
        def __init__(self):
            pass

        def read_text(self, file_name):
            if file_name == "top-level.txt":
                return None
            elif file_name == "RECORD":
                return """black/trans.cpython-39-darwin.so,sha256=<HASH>
black/trans.py,sha256=<HASH>
blackd/__init__.py,sha256=<HASH>
blackd/__main__.py,sha256=<HASH>
                """

    with patch("deptry.dependency.metadata.distribution") as mock:
        mock.return_value = MockDistribution()
        dependency = Dependency("Foo-bar")
        assert dependency.name == "Foo-bar"
        assert dependency.top_levels == set(["foo_bar", "black", "blackd"])
