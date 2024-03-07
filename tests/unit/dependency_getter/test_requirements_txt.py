from __future__ import annotations

from pathlib import Path

import pytest

from deptry.dependency_getter.requirements_txt import RequirementsTxtDependencyGetter
from tests.utils import run_within_dir


def test_parse_requirements_txt(tmp_path: Path) -> None:
    fake_requirements_txt = """click==8.1.3 #123asd
colorama==0.4.5
importlib-metadata==4.2.0 ; python_version >= "3.7" and python_version < "3.8"
isort==5.10.1, <6.0
toml==0.10.2
typing-extensions
zipp==3.8.1
foobar[foo, bar]
SomeProject ~= 1.4.2
SomeProject2 == 5.4 ; python_version < '3.8'
SomeProject3 ; sys_platform == 'win32'
requests [security] >= 2.8.1, == 2.8.* ; python_version < "2.7"
# This is a comment, to show how #-prefixed lines are ignored.
pytest
pytest-cov
beautifulsoup4
docopt == 0.6.1
requests [security] >= 2.8.1, == 2.8.* ; python_version < "2.7"
fox-python
httpx==0.25.2
"""
    with run_within_dir(tmp_path):
        with Path("requirements.txt").open("w") as f:
            f.write(fake_requirements_txt)

        getter = RequirementsTxtDependencyGetter(
            config=Path("pyproject.toml"),
            package_module_name_map={"fox-python": ("fox",)},
        )
        dependencies_extract = getter.get()
        dependencies = dependencies_extract.dependencies

        assert len(dependencies) == 19
        assert len(dependencies_extract.dev_dependencies) == 0

        assert dependencies[1].name == "colorama"
        assert not dependencies[1].is_conditional
        assert not dependencies[1].is_optional
        assert "colorama" in dependencies[1].top_levels

        assert dependencies[2].name == "importlib-metadata"
        assert dependencies[2].is_conditional
        assert not dependencies[2].is_optional
        assert "importlib_metadata" in dependencies[2].top_levels

        assert dependencies[11].name == "requests"
        assert dependencies[11].is_conditional
        assert dependencies[11].is_optional
        assert "requests" in dependencies[11].top_levels

        assert dependencies[17].name == "fox-python"
        assert not dependencies[17].is_conditional
        assert not dependencies[17].is_optional
        assert "fox" in dependencies[17].top_levels


def test_parse_requirements_txt_urls(tmp_path: Path) -> None:
    fake_requirements_txt = """urllib3 @ https://github.com/urllib3/urllib3/archive/refs/tags/1.26.8.zip
https://github.com/urllib3/urllib3/archive/refs/tags/1.26.8.zip
git+https://github.com/baz/foo-bar.git@asd#egg=foo-bar
git+https://github.com/baz/foo-bar.git@asd
git+https://github.com/abc123/bar-foo@xyz789#egg=bar-fooo"""

    with run_within_dir(tmp_path):
        with Path("requirements.txt").open("w") as f:
            f.write(fake_requirements_txt)

        dependencies_extract = RequirementsTxtDependencyGetter(Path("pyproject.toml")).get()
        dependencies = dependencies_extract.dependencies

        assert len(dependencies) == 5
        assert len(dependencies_extract.dev_dependencies) == 0

        assert dependencies[0].name == "urllib3"
        assert dependencies[1].name == "urllib3"
        assert dependencies[2].name == "foo-bar"
        assert dependencies[3].name == "foo-bar"
        assert dependencies[4].name == "bar-fooo"


def test_single(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        with Path("req.txt").open("w") as f:
            f.write("click==8.1.3 #123asd\ncolorama==0.4.5")

        dependencies_extract = RequirementsTxtDependencyGetter(
            Path("pyproject.toml"), requirements_txt=("req.txt",)
        ).get()
        dependencies = dependencies_extract.dependencies

        assert len(dependencies) == 2
        assert len(dependencies_extract.dev_dependencies) == 0

        assert dependencies[0].name == "click"
        assert dependencies[1].name == "colorama"


def test_multiple(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        with Path("foo.txt").open("w") as f:
            f.write("click==8.1.3 #123asd")

        with Path("bar.txt").open("w") as f:
            f.write("bar")

        dependencies_extract = RequirementsTxtDependencyGetter(
            Path("pyproject.toml"), requirements_txt=("foo.txt", "bar.txt")
        ).get()
        dependencies = dependencies_extract.dependencies

        assert len(dependencies) == 2
        assert len(dependencies_extract.dev_dependencies) == 0

        assert dependencies[0].name == "click"
        assert dependencies[1].name == "bar"


def test_dev_single(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        with Path("requirements.txt").open("w") as f:
            f.write("")

        with Path("requirements-dev.txt").open("w") as f:
            f.write("click==8.1.3 #123asd\ncolorama==0.4.5")

        dependencies_extract = RequirementsTxtDependencyGetter(Path("pyproject.toml")).get()
        dev_dependencies = dependencies_extract.dev_dependencies

        assert len(dependencies_extract.dependencies) == 0
        assert len(dev_dependencies) == 2

        assert dev_dependencies[1].name == "colorama"
        assert not dev_dependencies[1].is_conditional
        assert not dev_dependencies[1].is_optional
        assert "colorama" in dev_dependencies[1].top_levels


def test_dev_multiple(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        with Path("requirements.txt").open("w") as f:
            f.write("")

        with Path("requirements-dev.txt").open("w") as f:
            f.write("click==8.1.3 #123asd")

        with Path("dev-requirements.txt").open("w") as f:
            f.write("bar")

        dependencies_extract = RequirementsTxtDependencyGetter(Path("pyproject.toml")).get()
        dev_dependencies = dependencies_extract.dev_dependencies

        assert len(dependencies_extract.dependencies) == 0
        assert len(dev_dependencies) == 2

        assert "click" in [dev_dependencies[0].name, dev_dependencies[1].name]
        assert "bar" in [dev_dependencies[0].name, dev_dependencies[1].name]


def test_dev_multiple_with_arguments(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        with Path("requirements.txt").open("w") as f:
            f.write("")

        with Path("foo.txt").open("w") as f:
            f.write("click==8.1.3 #123asd")

        with Path("bar.txt").open("w") as f:
            f.write("bar")

        dependencies_extract = RequirementsTxtDependencyGetter(
            Path("pyproject.toml"), requirements_txt_dev=("foo.txt", "bar.txt")
        ).get()
        dev_dependencies = dependencies_extract.dev_dependencies

        assert len(dependencies_extract.dependencies) == 0
        assert len(dev_dependencies) == 2

        assert dev_dependencies[0].name == "click"
        assert dev_dependencies[1].name == "bar"


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("foo", False),
        ("http", False),
        ("https", False),
        ("httpx", False),
        ("git+http", False),
        ("git+https", False),
        ("http://", True),
        ("https://", True),
        ("git+http://", True),
        ("git+https://", True),
        ("file://", True),
        ("file:///", True),
        ("httpx://", True),
    ],
)
def test__line_is_url(line: str, expected: bool) -> None:
    assert RequirementsTxtDependencyGetter._line_is_url(line) is expected
