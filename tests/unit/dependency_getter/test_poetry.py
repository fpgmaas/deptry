from __future__ import annotations

from pathlib import Path

from deptry.dependency_getter.poetry import PoetryDependencyGetter
from tests.utils import run_within_dir


def test_dependency_getter(tmp_path: Path) -> None:
    fake_pyproject_toml = """
[tool.poetry.dependencies]
python = ">=3.7,<4.0"
bar =  { version = ">=2.5.1,<4.0.0", python = ">3.7" }
foo-bar =  { version = ">=2.5.1,<4.0.0", optional = true, python = ">3.7" }
fox-python = "*"  # top level module is called "fox"

[tool.poetry.dev-dependencies]
toml = "^0.10.2"
qux =  { version = ">=2.5.1,<4.0.0", optional = true }

[tool.poetry.group.lint.dependencies]
black = "^22.6.0"
mypy = "^1.3.0"

[tool.poetry.group.test.dependencies]
pytest = "^7.3.0"
pytest-cov = "^4.0.0"
"""

    with run_within_dir(tmp_path):
        with Path("pyproject.toml").open("w") as f:
            f.write(fake_pyproject_toml)

        getter = PoetryDependencyGetter(
            config=Path("pyproject.toml"),
            package_module_name_map={"fox-python": ("fox",)},
        )
        dependencies_extract = getter.get()
        dependencies = dependencies_extract.dependencies
        dev_dependencies = dependencies_extract.dev_dependencies

        assert len(dependencies) == 3
        assert len(dev_dependencies) == 6

        assert dependencies[0].name == "bar"
        assert dependencies[0].is_conditional
        assert not dependencies[0].is_optional
        assert "bar" in dependencies[0].top_levels

        assert dependencies[1].name == "foo-bar"
        assert dependencies[1].is_conditional
        assert dependencies[1].is_optional
        assert "foo_bar" in dependencies[1].top_levels

        assert dependencies[2].name == "fox-python"
        assert not dependencies[2].is_conditional
        assert not dependencies[2].is_optional
        assert "fox" in dependencies[2].top_levels

        assert dev_dependencies[0].name == "toml"
        assert not dev_dependencies[0].is_conditional
        assert not dev_dependencies[0].is_optional
        assert "toml" in dev_dependencies[0].top_levels

        assert dev_dependencies[1].name == "qux"
        assert not dev_dependencies[1].is_conditional
        assert dev_dependencies[1].is_optional
        assert "qux" in dev_dependencies[1].top_levels

        assert dev_dependencies[2].name == "black"
        assert not dev_dependencies[2].is_conditional
        assert not dev_dependencies[2].is_optional
        assert "black" in dev_dependencies[2].top_levels

        assert dev_dependencies[3].name == "mypy"
        assert not dev_dependencies[3].is_conditional
        assert not dev_dependencies[3].is_optional
        assert "mypy" in dev_dependencies[3].top_levels

        assert dev_dependencies[4].name == "pytest"
        assert not dev_dependencies[4].is_conditional
        assert not dev_dependencies[4].is_optional
        assert "pytest" in dev_dependencies[4].top_levels

        assert dev_dependencies[5].name == "pytest-cov"
        assert not dev_dependencies[5].is_conditional
        assert not dev_dependencies[5].is_optional
        assert "pytest_cov" in dev_dependencies[5].top_levels
