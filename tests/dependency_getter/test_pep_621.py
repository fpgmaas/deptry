from pathlib import Path

from deptry.dependency_getter.pep_621 import PEP621DependencyGetter
from deptry.utils import run_within_dir


def test_dependency_getter(tmp_path: Path) -> None:
    fake_pyproject_toml = """[project]
# PEP 621 project metadata
# See https://www.python.org/dev/peps/pep-0621/
dependencies = [
    "foo",
    "bar>=20.9",
    "optional-foo[option]>=0.12.11",
    "conditional-bar>=1.1.0; python_version < 3.11",
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
        with open("pyproject.toml", "w") as f:
            f.write(fake_pyproject_toml)

        dependencies = PEP621DependencyGetter().get().dependencies

        assert len(dependencies) == 7

        assert dependencies[0].name == "foo"
        assert not dependencies[0].is_conditional
        assert not dependencies[0].is_optional
        assert "foo" in dependencies[0].top_levels

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

        assert dependencies[4].name == "foobar"
        assert not dependencies[4].is_conditional
        assert not dependencies[4].is_optional
        assert "foobar" in dependencies[4].top_levels

        assert dependencies[5].name == "barfoo"
        assert not dependencies[5].is_conditional
        assert not dependencies[5].is_optional
        assert "barfoo" in dependencies[5].top_levels

        assert dependencies[6].name == "dep"
        assert not dependencies[6].is_conditional
        assert not dependencies[6].is_optional
        assert "dep" in dependencies[6].top_levels
