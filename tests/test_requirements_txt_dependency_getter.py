from deptry.dependency import Dependency
from deptry.dependency_getter.requirements_txt import RequirementsTxtDependencyGetter
from deptry.utils import run_within_dir


def test_parse_requirements_txt(tmp_path):

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
"""

    with run_within_dir(tmp_path):
        with open("requirements.txt", "w") as f:
            f.write(fake_requirements_txt)

        dependencies = RequirementsTxtDependencyGetter().get()

        assert len(dependencies) == 18

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

def test_parse_requirements_txt_urls(tmp_path):

    fake_requirements_txt = """
urllib3 @ https://github.com/urllib3/urllib3/archive/refs/tags/1.26.8.zip
https://github.com/urllib3/urllib3/archive/refs/tags/1.26.8.zip
git+https://github.com/baz/foo-bar.git@asd#egg=foo-bar
git+https://github.com/baz/foo-bar.git@asd
"""

    with run_within_dir(tmp_path):
        with open("requirements.txt", "w") as f:
            f.write(fake_requirements_txt)

        dependencies = RequirementsTxtDependencyGetter().get()

        assert len(dependencies) == 4
        assert dependencies[0].name == "urllib3"
        assert dependencies[1].name == "urllib3"
        assert dependencies[2].name == "foo-bar"
        assert dependencies[3].name == "foo-bar"


def test_with_name(tmp_path):

    with run_within_dir(tmp_path):
        with open("req.txt", "w") as f:
            f.write("click==8.1.3 #123asd\ncolorama==0.4.5")

        dependencies = RequirementsTxtDependencyGetter(requirements_txt="req.txt").get()
        assert len(dependencies) == 2
        assert dependencies[0].name == "click"
        assert dependencies[1].name == "colorama"


def test_dev_single(tmp_path):

    with run_within_dir(tmp_path):
        with open("requirements-dev.txt", "w") as f:
            f.write("click==8.1.3 #123asd\ncolorama==0.4.5")

        dependencies = RequirementsTxtDependencyGetter(dev=True).get()

        assert len(dependencies) == 2

        assert dependencies[1].name == "colorama"
        assert not dependencies[1].is_conditional
        assert not dependencies[1].is_optional
        assert "colorama" in dependencies[1].top_levels


def test_dev_multiple(tmp_path):

    with run_within_dir(tmp_path):
        with open("requirements-dev.txt", "w") as f:
            f.write("click==8.1.3 #123asd")
        with open("dev-requirements.txt", "w") as f:
            f.write("bar")

        dependencies = RequirementsTxtDependencyGetter(dev=True).get()
        assert len(dependencies) == 2
        assert "click" in [dependencies[0].name, dependencies[1].name]
        assert "bar" in [dependencies[0].name, dependencies[1].name]


def test_dev_multiple_with_arguments(tmp_path):

    with run_within_dir(tmp_path):
        with open("foo.txt", "w") as f:
            f.write("click==8.1.3 #123asd")
        with open("bar.txt", "w") as f:
            f.write("bar")

        dependencies = RequirementsTxtDependencyGetter(dev=True, requirements_txt_dev=["foo.txt", "bar.txt"]).get()
        assert len(dependencies) == 2
        assert dependencies[0].name == "click"
        assert dependencies[1].name == "bar"
