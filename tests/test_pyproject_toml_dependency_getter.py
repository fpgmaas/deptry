from deptry.dependency import Dependency
from deptry.dependency_getter.pyproject_toml import PyprojectTomlDependencyGetter
from deptry.utils import run_within_dir


def test_dependency_getter(tmp_path):
    fake_pyproject_toml = """[tool.poetry.dependencies]
python = ">=3.7,<4.0"
toml = "^0.10.2"
foo =  { version = ">=2.5.1,<4.0.0", optional = true }
bar =  { version = ">=2.5.1,<4.0.0", python = ">3.7" }
foo-bar =  { version = ">=2.5.1,<4.0.0", optional = true, python = ">3.7" }"""

    with run_within_dir(tmp_path):
        with open("pyproject.toml", "w") as f:
            f.write(fake_pyproject_toml)

        dependencies = PyprojectTomlDependencyGetter().get()

        assert len(dependencies) == 4

        assert dependencies[0].name == "toml"
        assert not dependencies[0].is_conditional
        assert not dependencies[0].is_optional
        assert "toml" in dependencies[0].top_levels

        assert dependencies[1].name == "foo"
        assert not dependencies[1].is_conditional
        assert dependencies[1].is_optional
        assert "foo" in dependencies[1].top_levels

        assert dependencies[2].name == "bar"
        assert dependencies[2].is_conditional
        assert not dependencies[2].is_optional
        assert "bar" in dependencies[2].top_levels

        assert dependencies[3].name == "foo-bar"
        assert dependencies[3].is_conditional
        assert dependencies[3].is_optional
        assert "foo_bar" in dependencies[3].top_levels


def test_dependency_getter_dev(tmp_path):
    fake_pyproject_toml = """[tool.poetry.dev-dependencies]
toml = "^0.10.2"
foo =  { version = ">=2.5.1,<4.0.0", optional = true }
"""

    with run_within_dir(tmp_path):
        with open("pyproject.toml", "w") as f:
            f.write(fake_pyproject_toml)

        dependencies = PyprojectTomlDependencyGetter(dev=True).get()

        assert len(dependencies) == 2

        assert dependencies[0].name == "toml"
        assert not dependencies[0].is_conditional
        assert not dependencies[0].is_optional
        assert "toml" in dependencies[0].top_levels

        assert dependencies[1].name == "foo"
        assert not dependencies[1].is_conditional
        assert dependencies[1].is_optional
        assert "foo" in dependencies[1].top_levels
