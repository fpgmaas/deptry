from __future__ import annotations

from pathlib import Path

from deptry.dependency_getter.pep621.uv import UvDependencyGetter
from tests.utils import run_within_dir


def test_dependency_getter(tmp_path: Path) -> None:
    fake_pyproject_toml = """\
[project]
# PEP 621 project metadata
# See https://www.python.org/dev/peps/pep-0621/
dependencies = [
    "qux",
    "bar>=20.9",
    "optional-foo[option]>=0.12.11",
    "conditional-bar>=1.1.0; python_version < '3.11'",
    "fox-python",  # top level module is called "fox"
]

[dependency-groups]
dev-group = ["foo", "baz"]
all = [{include-group = "dev-group"}, "foobaz"]

[tool.uv]
dev-dependencies = [
    "qux",
    "bar; python_version < '3.11'",
    "foo-bar",
]
"""

    with run_within_dir(tmp_path):
        with Path("pyproject.toml").open("w") as f:
            f.write(fake_pyproject_toml)

        dependencies_extract = UvDependencyGetter(
            config=Path("pyproject.toml"),
            package_module_name_map={"fox-python": ("fox",)},
        ).get()

        dependencies = dependencies_extract.dependencies
        dev_dependencies = dependencies_extract.dev_dependencies

        assert len(dependencies) == 5
        assert len(dev_dependencies) == 6

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

        assert dev_dependencies[0].name == "foo"
        assert "foo" in dev_dependencies[0].top_levels

        assert dev_dependencies[1].name == "baz"
        assert "baz" in dev_dependencies[1].top_levels

        assert dev_dependencies[2].name == "foobaz"
        assert "foobaz" in dev_dependencies[2].top_levels

        assert dev_dependencies[3].name == "qux"
        assert "qux" in dev_dependencies[3].top_levels

        assert dev_dependencies[4].name == "bar"
        assert "bar" in dev_dependencies[4].top_levels

        assert dev_dependencies[5].name == "foo-bar"
        assert "foo_bar" in dev_dependencies[5].top_levels
