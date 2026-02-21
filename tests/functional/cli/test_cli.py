from __future__ import annotations

import sys
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from click.testing import CliRunner
from inline_snapshot import snapshot

from deptry.cli import cli
from tests.functional.utils import Project
from tests.utils import get_issues_report

if TYPE_CHECKING:
    from tests.utils import PoetryVenvFactory


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_returns_error(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run_deptry(f". -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == snapshot([
            {
                "error": {"code": "DEP002", "message": "'isort' defined as a dependency but not used in the codebase"},
                "module": "isort",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "'requests' defined as a dependency but not used in the codebase",
                },
                "module": "requests",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {"code": "DEP004", "message": "'black' imported but declared as a dev dependency"},
                "module": "black",
                "location": {"file": "src/main.py", "line": 4, "column": 8},
            },
            {
                "error": {"code": "DEP001", "message": "'white' imported but missing from the dependency definitions"},
                "module": "white",
                "location": {"file": "src/main.py", "line": 6, "column": 8},
            },
        ])


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_ignore_notebooks(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run_deptry(f". --ignore-notebooks -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == snapshot([
            {
                "error": {"code": "DEP002", "message": "'arrow' defined as a dependency but not used in the codebase"},
                "module": "arrow",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {"code": "DEP002", "message": "'isort' defined as a dependency but not used in the codebase"},
                "module": "isort",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "'requests' defined as a dependency but not used in the codebase",
                },
                "module": "requests",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {"code": "DEP004", "message": "'black' imported but declared as a dev dependency"},
                "module": "black",
                "location": {"file": "src/main.py", "line": 4, "column": 8},
            },
            {
                "error": {"code": "DEP001", "message": "'white' imported but missing from the dependency definitions"},
                "module": "white",
                "location": {"file": "src/main.py", "line": 6, "column": 8},
            },
        ])


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_ignore_flags(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        result = virtual_env.run_deptry(". --per-rule-ignores DEP001=white,DEP002=isort|pkginfo|requests,DEP004=black")

        assert result.returncode == 0


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_ignore_flag(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        result = virtual_env.run_deptry(". --ignore DEP001,DEP002,DEP003,DEP004")

        assert result.returncode == 0


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_exclude(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run_deptry(f". --exclude src/notebook.ipynb -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == snapshot([
            {
                "error": {"code": "DEP002", "message": "'arrow' defined as a dependency but not used in the codebase"},
                "module": "arrow",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {"code": "DEP002", "message": "'isort' defined as a dependency but not used in the codebase"},
                "module": "isort",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "'requests' defined as a dependency but not used in the codebase",
                },
                "module": "requests",
                "location": {
                    "file": "pyproject.toml",
                    "line": None,
                    "column": None,
                },
            },
            {
                "error": {"code": "DEP004", "message": "'black' imported but declared as a dev dependency"},
                "module": "black",
                "location": {
                    "file": "src/main.py",
                    "line": 4,
                    "column": 8,
                },
            },
            {
                "error": {"code": "DEP001", "message": "'white' imported but missing from the dependency definitions"},
                "module": "white",
                "location": {
                    "file": "src/main.py",
                    "line": 6,
                    "column": 8,
                },
            },
        ])


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_extend_exclude(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run_deptry(f". -ee src/notebook.ipynb -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == snapshot([
            {
                "error": {"code": "DEP002", "message": "'arrow' defined as a dependency but not used in the codebase"},
                "module": "arrow",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {"code": "DEP002", "message": "'isort' defined as a dependency but not used in the codebase"},
                "module": "isort",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "'requests' defined as a dependency but not used in the codebase",
                },
                "module": "requests",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {"code": "DEP004", "message": "'black' imported but declared as a dev dependency"},
                "module": "black",
                "location": {"file": "src/main.py", "line": 4, "column": 8},
            },
            {
                "error": {"code": "DEP001", "message": "'white' imported but missing from the dependency definitions"},
                "module": "white",
                "location": {"file": "src/main.py", "line": 6, "column": 8},
            },
        ])


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_known_first_party(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run_deptry(f". --known-first-party white -o {issue_report}")

        assert result.returncode == 1
        assert get_issues_report(Path(issue_report)) == snapshot([
            {
                "error": {"code": "DEP002", "message": "'isort' defined as a dependency but not used in the codebase"},
                "module": "isort",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "'requests' defined as a dependency but not used in the codebase",
                },
                "module": "requests",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {"code": "DEP004", "message": "'black' imported but declared as a dev dependency"},
                "module": "black",
                "location": {"file": "src/main.py", "line": 4, "column": 8},
            },
        ])


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_not_verbose(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run_deptry(f". --no-ansi -o {issue_report}")

        assert result.returncode == 1
        assert "The project contains the following dependencies:" not in result.stderr
        assert get_issues_report(Path(issue_report)) == snapshot([
            {
                "error": {"code": "DEP002", "message": "'isort' defined as a dependency but not used in the codebase"},
                "module": "isort",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "'requests' defined as a dependency but not used in the codebase",
                },
                "module": "requests",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {"code": "DEP004", "message": "'black' imported but declared as a dev dependency"},
                "module": "black",
                "location": {"file": "src/main.py", "line": 4, "column": 8},
            },
            {
                "error": {"code": "DEP001", "message": "'white' imported but missing from the dependency definitions"},
                "module": "white",
                "location": {"file": "src/main.py", "line": 6, "column": 8},
            },
        ])


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_verbose(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run_deptry(f". --no-ansi --verbose -o {issue_report}")

        assert result.returncode == 1
        assert "The project contains the following dependencies:" in result.stderr
        assert "The project contains the following dev dependencies:" in result.stderr
        assert get_issues_report(Path(issue_report)) == snapshot([
            {
                "error": {"code": "DEP002", "message": "'isort' defined as a dependency but not used in the codebase"},
                "module": "isort",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "'requests' defined as a dependency but not used in the codebase",
                },
                "module": "requests",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {"code": "DEP004", "message": "'black' imported but declared as a dev dependency"},
                "module": "black",
                "location": {"file": "src/main.py", "line": 4, "column": 8},
            },
            {
                "error": {"code": "DEP001", "message": "'white' imported but missing from the dependency definitions"},
                "module": "white",
                "location": {"file": "src/main.py", "line": 6, "column": 8},
            },
        ])


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_with_not_json_output(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        json_files_count = len(list(Path().glob("*.json")))

        result = virtual_env.run_deptry(". --no-ansi")

        assert result.returncode == 1
        # Assert that we have the same number of JSON files as before running the command.
        assert len(list(Path().glob("*.json"))) == json_files_count
        assert result.stderr == snapshot("""\
Scanning 2 files...

pyproject.toml: DEP002 'isort' defined as a dependency but not used in the codebase
pyproject.toml: DEP002 'requests' defined as a dependency but not used in the codebase
src/main.py:4:8: DEP004 'black' imported but declared as a dev dependency
src/main.py:6:8: DEP001 'white' imported but missing from the dependency definitions
Found 4 dependency issues.

For more information, see the documentation: https://deptry.com/
""")


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_with_json_output(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run_deptry(f". --no-ansi -o {issue_report}")

        # Assert that we still write to console when generating a JSON report.
        assert result.stderr == snapshot("""\
Scanning 2 files...

pyproject.toml: DEP002 'isort' defined as a dependency but not used in the codebase
pyproject.toml: DEP002 'requests' defined as a dependency but not used in the codebase
src/main.py:4:8: DEP004 'black' imported but declared as a dev dependency
src/main.py:6:8: DEP001 'white' imported but missing from the dependency definitions
Found 4 dependency issues.

For more information, see the documentation: https://deptry.com/
""")
        assert get_issues_report(Path(issue_report)) == snapshot([
            {
                "error": {"code": "DEP002", "message": "'isort' defined as a dependency but not used in the codebase"},
                "module": "isort",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "'requests' defined as a dependency but not used in the codebase",
                },
                "module": "requests",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {"code": "DEP004", "message": "'black' imported but declared as a dev dependency"},
                "module": "black",
                "location": {"file": "src/main.py", "line": 4, "column": 8},
            },
            {
                "error": {"code": "DEP001", "message": "'white' imported but missing from the dependency definitions"},
                "module": "white",
                "location": {"file": "src/main.py", "line": 6, "column": 8},
            },
        ])


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_with_github_output(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        result = virtual_env.run_deptry(". --no-ansi --github-output")

        assert result.returncode == 1
        assert result.stderr == snapshot("""\
Scanning 2 files...

pyproject.toml: DEP002 'isort' defined as a dependency but not used in the codebase
pyproject.toml: DEP002 'requests' defined as a dependency but not used in the codebase
src/main.py:4:8: DEP004 'black' imported but declared as a dev dependency
src/main.py:6:8: DEP001 'white' imported but missing from the dependency definitions
Found 4 dependency issues.

For more information, see the documentation: https://deptry.com/
::error file=pyproject.toml,line=1,title=DEP002::'isort' defined as a dependency but not used in the codebase
::error file=pyproject.toml,line=1,title=DEP002::'requests' defined as a dependency but not used in the codebase
::error file=src/main.py,line=4,col=8,title=DEP004::'black' imported but declared as a dev dependency
::error file=src/main.py,line=6,col=8,title=DEP001::'white' imported but missing from the dependency definitions
""")


@pytest.mark.xdist_group(name=Project.EXAMPLE)
def test_cli_with_github_output_warning_errors(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        result = virtual_env.run_deptry(". --no-ansi --github-output --github-warning-errors DEP001,DEP004")

        assert result.returncode == 1
        assert result.stderr == snapshot("""\
Scanning 2 files...

pyproject.toml: DEP002 'isort' defined as a dependency but not used in the codebase
pyproject.toml: DEP002 'requests' defined as a dependency but not used in the codebase
src/main.py:4:8: DEP004 'black' imported but declared as a dev dependency
src/main.py:6:8: DEP001 'white' imported but missing from the dependency definitions
Found 4 dependency issues.

For more information, see the documentation: https://deptry.com/
::error file=pyproject.toml,line=1,title=DEP002::'isort' defined as a dependency but not used in the codebase
::error file=pyproject.toml,line=1,title=DEP002::'requests' defined as a dependency but not used in the codebase
::warning file=src/main.py,line=4,col=8,title=DEP004::'black' imported but declared as a dev dependency
::warning file=src/main.py,line=6,col=8,title=DEP001::'white' imported but missing from the dependency definitions
""")


def test_cli_config_does_not_supress_output(poetry_venv_factory: PoetryVenvFactory) -> None:
    """Regression test that ensures that passing `--config` option does not suppress output."""
    with poetry_venv_factory(Project.WITHOUT_DEPTRY_OPTION) as virtual_env:
        result = virtual_env.run_deptry(". --no-ansi --config pyproject.toml")

        assert result.returncode == 1
        assert result.stderr == snapshot("""\
Scanning 0 file...

pyproject.toml: DEP002 'isort' defined as a dependency but not used in the codebase
Found 1 dependency issue.

For more information, see the documentation: https://deptry.com/
""")


def test_cli_help() -> None:
    result = CliRunner().invoke(cli, "--help")

    assert result.exit_code == 0


@pytest.mark.xdist_group(name=Project.EXAMPLE)
@pytest.mark.skipif(sys.platform != "win32", reason="Explicitly tests paths output for Windows systems")
def test_cli_paths_respect_windows(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run_deptry(f". --no-ansi -o {issue_report} --github-output", enforce_posix_paths=False)

        assert result.returncode == 1
        assert result.stderr == snapshot("""\
Scanning 2 files...

pyproject.toml: DEP002 'isort' defined as a dependency but not used in the codebase
pyproject.toml: DEP002 'requests' defined as a dependency but not used in the codebase
src\\main.py:4:8: DEP004 'black' imported but declared as a dev dependency
src\\main.py:6:8: DEP001 'white' imported but missing from the dependency definitions
Found 4 dependency issues.

For more information, see the documentation: https://deptry.com/
::error file=pyproject.toml,line=1,title=DEP002::'isort' defined as a dependency but not used in the codebase
::error file=pyproject.toml,line=1,title=DEP002::'requests' defined as a dependency but not used in the codebase
::error file=src\\main.py,line=4,col=8,title=DEP004::'black' imported but declared as a dev dependency
::error file=src\\main.py,line=6,col=8,title=DEP001::'white' imported but missing from the dependency definitions
""")

        assert get_issues_report(Path(issue_report)) == snapshot([
            {
                "error": {"code": "DEP002", "message": "'isort' defined as a dependency but not used in the codebase"},
                "module": "isort",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "'requests' defined as a dependency but not used in the codebase",
                },
                "module": "requests",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {"code": "DEP004", "message": "'black' imported but declared as a dev dependency"},
                "module": "black",
                "location": {"file": "src\\main.py", "line": 4, "column": 8},
            },
            {
                "error": {"code": "DEP001", "message": "'white' imported but missing from the dependency definitions"},
                "module": "white",
                "location": {"file": "src\\main.py", "line": 6, "column": 8},
            },
        ])


@pytest.mark.xdist_group(name=Project.EXAMPLE)
@pytest.mark.skipif(sys.platform == "win32", reason="Explicitly tests paths output for non-Windows systems")
def test_cli_paths_respect_non_windows(poetry_venv_factory: PoetryVenvFactory) -> None:
    with poetry_venv_factory(Project.EXAMPLE) as virtual_env:
        issue_report = f"{uuid.uuid4()}.json"
        result = virtual_env.run_deptry(f". --no-ansi -o {issue_report} --github-output", enforce_posix_paths=False)

        assert result.returncode == 1
        assert result.stderr == snapshot("""\
Scanning 2 files...

pyproject.toml: DEP002 'isort' defined as a dependency but not used in the codebase
pyproject.toml: DEP002 'requests' defined as a dependency but not used in the codebase
src/main.py:4:8: DEP004 'black' imported but declared as a dev dependency
src/main.py:6:8: DEP001 'white' imported but missing from the dependency definitions
Found 4 dependency issues.

For more information, see the documentation: https://deptry.com/
::error file=pyproject.toml,line=1,title=DEP002::'isort' defined as a dependency but not used in the codebase
::error file=pyproject.toml,line=1,title=DEP002::'requests' defined as a dependency but not used in the codebase
::error file=src/main.py,line=4,col=8,title=DEP004::'black' imported but declared as a dev dependency
::error file=src/main.py,line=6,col=8,title=DEP001::'white' imported but missing from the dependency definitions
""")

        assert get_issues_report(Path(issue_report)) == snapshot([
            {
                "error": {"code": "DEP002", "message": "'isort' defined as a dependency but not used in the codebase"},
                "module": "isort",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {
                    "code": "DEP002",
                    "message": "'requests' defined as a dependency but not used in the codebase",
                },
                "module": "requests",
                "location": {"file": "pyproject.toml", "line": None, "column": None},
            },
            {
                "error": {"code": "DEP004", "message": "'black' imported but declared as a dev dependency"},
                "module": "black",
                "location": {"file": "src/main.py", "line": 4, "column": 8},
            },
            {
                "error": {"code": "DEP001", "message": "'white' imported but missing from the dependency definitions"},
                "module": "white",
                "location": {"file": "src/main.py", "line": 6, "column": 8},
            },
        ])
