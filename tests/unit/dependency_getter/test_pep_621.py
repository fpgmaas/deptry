from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from deptry.dependency_getter.pep_621 import PEP621DependencyGetter
from tests.utils import run_within_dir

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture


def test_dependency_getter(tmp_path: Path) -> None:
    fake_pyproject_toml = """[project]
# PEP 621 project metadata
# See https://www.python.org/dev/peps/pep-0621/
dependencies = [
    "qux",
    "bar>=20.9",
    "optional-foo[option]>=0.12.11",
    "conditional-bar>=1.1.0; python_version < 3.11",
    "fox-python",  # top level module is called "fox"
]

[project.optional-dependencies]
group1 = [
    "foobar",
    "barfoo",
]
group2 = [
    "dep",
]
"""

    with run_within_dir(tmp_path):
        with Path("pyproject.toml").open("w") as f:
            f.write(fake_pyproject_toml)

        getter = PEP621DependencyGetter(
            config=Path("pyproject.toml"),
            package_module_name_map={"fox-python": ("fox",)},
        )
        dependencies = getter.get().dependencies

        assert len(dependencies) == 8

        assert dependencies[0].name == "qux"
        assert "qux" in dependencies[0].top_levels

        assert dependencies[1].name == "bar"
        assert "bar" in dependencies[1].top_levels

        assert dependencies[2].name == "optional-foo"
        assert "optional_foo" in dependencies[2].top_levels

        assert dependencies[3].name == "conditional-bar"
        assert "conditional_bar" in dependencies[3].top_levels

        assert dependencies[4].name == "fox-python"
        assert "fox" in dependencies[4].top_levels

        assert dependencies[5].name == "foobar"
        assert "foobar" in dependencies[5].top_levels

        assert dependencies[6].name == "barfoo"
        assert "barfoo" in dependencies[6].top_levels

        assert dependencies[7].name == "dep"
        assert "dep" in dependencies[7].top_levels


def test_dependency_getter_with_dev_dependencies(tmp_path: Path) -> None:
    fake_pyproject_toml = """[project]
# PEP 621 project metadata
# See https://www.python.org/dev/peps/pep-0621/
dependencies = [
"qux",
]

[project.optional-dependencies]
group1 = [
    "foobar",
]
group2 = [
    "barfoo",
]
"""

    with run_within_dir(tmp_path):
        with Path("pyproject.toml").open("w") as f:
            f.write(fake_pyproject_toml)

        getter = PEP621DependencyGetter(config=Path("pyproject.toml"), pep621_dev_dependency_groups=("group2",))
        dependencies = getter.get().dependencies
        dev_dependencies = getter.get().dev_dependencies

        assert len(dependencies) == 2

        assert dependencies[0].name == "qux"
        assert "qux" in dependencies[0].top_levels

        assert dependencies[1].name == "foobar"
        assert "foobar" in dependencies[1].top_levels

        assert len(dev_dependencies) == 1
        assert dev_dependencies[0].name == "barfoo"
        assert "barfoo" in dev_dependencies[0].top_levels


def test_dependency_getter_with_incorrect_dev_group(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    fake_pyproject_toml = """[project]
# PEP 621 project metadata
# See https://www.python.org/dev/peps/pep-0621/
dependencies = [
"qux",
]

[project.optional-dependencies]
group1 = [
    "foobar",
]
group2 = [
    "barfoo",
]
"""

    with run_within_dir(tmp_path), caplog.at_level(logging.INFO):
        with Path("pyproject.toml").open("w") as f:
            f.write(fake_pyproject_toml)

        getter = PEP621DependencyGetter(config=Path("pyproject.toml"), pep621_dev_dependency_groups=("group3",))
        dependencies = getter.get().dependencies

        assert (
            "Trying to extract the dependencies from the optional dependency groups ['group3'] as development dependencies, but the following groups were not found: ['group3']"
            in caplog.text
        )

        assert len(dependencies) == 3

        assert dependencies[0].name == "qux"
        assert "qux" in dependencies[0].top_levels

        assert dependencies[1].name == "foobar"
        assert "foobar" in dependencies[1].top_levels

        assert dependencies[2].name == "barfoo"
        assert "barfoo" in dependencies[2].top_levels


def test_dependency_getter_empty_dependencies(tmp_path: Path) -> None:
    fake_pyproject_toml = """[project]
# PEP 621 project metadata
# See https://www.python.org/dev/peps/pep-0621/
"""

    with run_within_dir(tmp_path):
        with Path("pyproject.toml").open("w") as f:
            f.write(fake_pyproject_toml)

        getter = PEP621DependencyGetter(config=Path("pyproject.toml"))
        dependencies_extract = getter.get()

        assert len(dependencies_extract.dependencies) == 0
        assert len(dependencies_extract.dev_dependencies) == 0
