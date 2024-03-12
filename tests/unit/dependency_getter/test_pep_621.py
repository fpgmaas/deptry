from __future__ import annotations

from pathlib import Path

from deptry.dependency_getter.pep_621 import PEP621DependencyGetter
from tests.utils import run_within_dir


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
        assert not dependencies[0].is_conditional
        assert not dependencies[0].is_optional
        assert "qux" in dependencies[0].top_levels

        assert dependencies[1].name == "bar"
        assert not dependencies[1].is_conditional
        assert not dependencies[1].is_optional
        assert "bar" in dependencies[1].top_levels

        assert dependencies[2].name == "optional-foo"
        assert not dependencies[2].is_conditional
        assert dependencies[2].is_optional
        assert "optional_foo" in dependencies[2].top_levels

        assert dependencies[3].name == "conditional-bar"
        assert dependencies[3].is_conditional
        assert not dependencies[3].is_optional
        assert "conditional_bar" in dependencies[3].top_levels

        assert dependencies[4].name == "fox-python"
        assert not dependencies[4].is_conditional
        assert not dependencies[4].is_optional
        assert "fox" in dependencies[4].top_levels

        assert dependencies[5].name == "foobar"
        assert not dependencies[5].is_conditional
        assert not dependencies[5].is_optional
        assert "foobar" in dependencies[5].top_levels

        assert dependencies[6].name == "barfoo"
        assert not dependencies[6].is_conditional
        assert not dependencies[6].is_optional
        assert "barfoo" in dependencies[6].top_levels

        assert dependencies[7].name == "dep"
        assert not dependencies[7].is_conditional
        assert not dependencies[7].is_optional
        assert "dep" in dependencies[7].top_levels
