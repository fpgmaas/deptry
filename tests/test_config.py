from distutils.command.config import config

from deptry.config import Config
from deptry.utils import run_within_dir


def test_ignore_attributes(tmp_path):

    fake_pyproject_toml = """[tool.deptry]
ignore_obsolete = [
  'foo'
]
ignore_missing = [
  'foo2', 'foo3'
]
ignore_transitive = [
  'foo4'
]
ignore_misplaced_dev = [
  'foo5'
]"""

    with run_within_dir(tmp_path):
        with open("pyproject.toml", "w") as f:
            f.write(fake_pyproject_toml)

        config = Config(ignore_obsolete="", ignore_missing=None)

        assert config.ignore_obsolete == ["foo"]
        assert config.ignore_missing == ["foo2", "foo3"]
        assert config.ignore_transitive == ["foo4"]
        assert config.ignore_misplaced_dev == ["foo5"]

        config = Config(ignore_obsolete="bar,bar2", ignore_misplaced_dev="bar3")
        assert config.ignore_obsolete == ["bar", "bar2"]
        assert config.ignore_missing == ["foo2", "foo3"]
        assert config.ignore_transitive == ["foo4"]
        assert config.ignore_misplaced_dev == ["bar3"]


def test_exclude_attribute(tmp_path):

    fake_pyproject_toml = """[tool.deptry]
exclude = [
  '.venv','docs','tests'
]
"""

    with run_within_dir(tmp_path):
        with open("pyproject.toml", "w") as f:
            f.write(fake_pyproject_toml)

        config = Config(exclude="")
        assert config.exclude == [".venv", "docs", "tests"]
        config = Config()
        assert config.exclude == [".venv", "docs", "tests"]
        config = Config(exclude="foo,bar")
        assert config.exclude == ["foo", "bar"]


def test_extend_exclude_attribute(tmp_path):

    fake_pyproject_toml = """[tool.deptry]
exclude = [
  '.venv','docs','tests'
]
extend_exclude = [
  'foo'
]
"""

    with run_within_dir(tmp_path):
        with open("pyproject.toml", "w") as f:
            f.write(fake_pyproject_toml)

        config = Config(extend_exclude="")
        assert config.extend_exclude == ["foo"]
        config = Config(extend_exclude="bar,barr")
        assert config.extend_exclude == ["bar", "barr"]


def test_skip_attributes(tmp_path):

    with run_within_dir(tmp_path):

        with open("pyproject.toml", "w") as f:
            f.write("")

        # empty pyproject.toml, no arguments, so should all be False
        config = Config()
        assert not config.skip_obsolete
        assert not config.skip_transitive
        assert not config.skip_missing
        assert not config.skip_misplaced_dev

        # Test that passing attributes works.
        config = Config(skip_obsolete=True, skip_missing=True, skip_transitive=True, skip_misplaced_dev=True)
        assert config.skip_obsolete
        assert config.skip_transitive
        assert config.skip_missing
        assert config.skip_misplaced_dev

        fake_pyproject_toml = """[tool.deptry]
skip_obsolete = true
skip_missing = true
skip_transitive = true
skip_misplaced_dev = true
"""
        with open("pyproject.toml", "w") as f:
            f.write(fake_pyproject_toml)

        # Test that reading from pyproject.toml works
        config = Config()
        assert config.skip_obsolete
        assert config.skip_transitive
        assert config.skip_missing
        assert config.skip_misplaced_dev
