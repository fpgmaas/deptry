from __future__ import annotations

from pathlib import Path

import pytest

from deptry.core import Core
from tests.utils import create_files_from_list_of_dicts, run_within_dir


@pytest.mark.parametrize(
    ("known_first_party", "root_suffix", "expected"),
    [
        (
            (),
            "",
            {"module_with_init"},
        ),
        (
            ("module_without_init",),
            "",
            {"module_with_init", "module_without_init"},
        ),
        (
            ("module_with_init", "module_without_init"),
            "",
            {"module_with_init", "module_without_init"},
        ),
        (
            ("module_without_init",),
            "module_with_init",
            {"module_without_init", "subdirectory"},
        ),
    ],
)
def test__get_local_modules(
    tmp_path: Path, known_first_party: tuple[str, ...], root_suffix: str, expected: set[str]
) -> None:
    with run_within_dir(tmp_path):
        paths = [
            {"dir": "module_with_init", "file": "__init__.py"},
            {"dir": "module_with_init", "file": "foo.py"},
            {"dir": "module_with_init/subdirectory", "file": "__init__.py"},
            {"dir": "module_with_init/subdirectory", "file": "foo.py"},
            {"dir": "module_without_init", "file": "foo.py"},
        ]
        create_files_from_list_of_dicts(paths)

        assert (
            Core(
                root=tmp_path / root_suffix,
                config=Path("pyproject.toml"),
                ignore_obsolete=(),
                ignore_missing=(),
                ignore_transitive=(),
                ignore_misplaced_dev=(),
                skip_obsolete=False,
                skip_missing=False,
                skip_transitive=False,
                skip_misplaced_dev=False,
                exclude=(),
                extend_exclude=(),
                using_default_exclude=True,
                ignore_notebooks=False,
                requirements_txt=(),
                requirements_txt_dev=(),
                known_first_party=known_first_party,
                json_output="",
            )._get_local_modules()
            == expected
        )


def test__exit_with_issues() -> None:
    issues = {
        "missing": ["foo"],
        "obsolete": ["foo"],
        "transitive": ["foo"],
        "misplaced_dev": ["foo"],
    }
    with pytest.raises(SystemExit) as e:
        Core._exit(issues)

    assert e.type == SystemExit
    assert e.value.code == 1


def test__exit_without_issues() -> None:
    issues: dict[str, list[str]] = {}
    with pytest.raises(SystemExit) as e:
        Core._exit(issues)

    assert e.type == SystemExit
    assert e.value.code == 0
