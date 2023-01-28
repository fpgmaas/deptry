from __future__ import annotations

from pathlib import Path

from deptry.dependency_getter.pdm import PDMDependencyGetter
from tests.utils import run_within_dir


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
"""

    with run_within_dir(tmp_path):
        with open("pyproject.toml", "w") as f:
            f.write(fake_pyproject_toml)

        dependencies = PDMDependencyGetter(Path("pyproject.toml")).get().dependencies

        assert len(dependencies) == 4

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


def test_dev_dependency_getter(tmp_path: Path) -> None:
    fake_pyproject_toml = """[project]
# PEP 621 project metadata
# See https://www.python.org/dev/peps/pep-0621/
dependencies = [
    "foo",
    "bar>=20.9",
    "optional-foo[option]>=0.12.11",
    "conditional-bar>=1.1.0; python_version < 3.11",
]
[tool.pdm.dev-dependencies]
test = [
    "foo",
    "bar; python_version < 3.11"
    ]
tox = [
    "foo-bar",
]
"""

    with run_within_dir(tmp_path):
        with open("pyproject.toml", "w") as f:
            f.write(fake_pyproject_toml)

        dev_dependencies = PDMDependencyGetter(Path("pyproject.toml")).get().dev_dependencies

        assert len(dev_dependencies) == 3

        assert dev_dependencies[0].name == "foo"
        assert not dev_dependencies[0].is_conditional
        assert not dev_dependencies[0].is_optional
        assert "foo" in dev_dependencies[0].top_levels

        assert dev_dependencies[1].name == "bar"
        assert dev_dependencies[1].is_conditional
        assert not dev_dependencies[1].is_optional
        assert "bar" in dev_dependencies[1].top_levels

        assert dev_dependencies[2].name == "foo-bar"
        assert not dev_dependencies[2].is_conditional
        assert not dev_dependencies[2].is_optional
        assert "foo_bar" in dev_dependencies[2].top_levels
