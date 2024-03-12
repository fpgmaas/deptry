from __future__ import annotations

from pathlib import Path

import pytest
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern

from deptry.python_file_finder import PythonFileFinder
from tests.utils import create_files, run_within_dir


def test_simple(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        create_files([
            Path("dir/subdir/file1.py"),
            Path("dir/subdir/file2.py"),
            Path("dir/subdir/file3.py"),
            Path("other_dir/subdir/file1.py"),
            Path("other_dir/subdir/file2.py"),
        ])

        files = PythonFileFinder(
            exclude=(".venv",), extend_exclude=("other_dir",), using_default_exclude=False
        ).get_all_python_files_in((Path(),))

        assert sorted(files) == [
            Path("dir/subdir/file1.py"),
            Path("dir/subdir/file2.py"),
            Path("dir/subdir/file3.py"),
        ]


def test_only_matches_start(tmp_path: Path) -> None:
    """
    Test that adding 'subdir' as exclude argument does not also exclude dir/subdir.
    """
    with run_within_dir(tmp_path):
        create_files([
            Path("dir/subdir/file1.py"),
            Path("dir/subdir/file2.py"),
            Path("dir/subdir/file3.py"),
            Path("subdir/file1.py"),
            Path("subdir/file2.py"),
        ])

        files = PythonFileFinder(
            exclude=("subdir",), extend_exclude=(), using_default_exclude=False
        ).get_all_python_files_in((Path(),))

        assert sorted(files) == [
            Path("dir/subdir/file1.py"),
            Path("dir/subdir/file2.py"),
            Path("dir/subdir/file3.py"),
        ]


@pytest.mark.parametrize(
    ("ignore_notebooks", "expected"),
    [
        (
            False,
            [Path("dir/subdir/file1.ipynb")],
        ),
        (
            True,
            [],
        ),
    ],
)
def test_matches_ipynb(ignore_notebooks: bool, expected: list[Path], tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        create_files([Path("dir/subdir/file1.ipynb")])

        files = PythonFileFinder(
            exclude=(), extend_exclude=(), using_default_exclude=False, ignore_notebooks=ignore_notebooks
        ).get_all_python_files_in((Path(),))

        assert sorted(files) == expected


@pytest.mark.parametrize(
    ("exclude", "expected"),
    [
        (
            (".*file1",),
            [
                Path(".cache/file2.py"),
                Path("dir/subdir/file2.py"),
                Path("dir/subdir/file3.py"),
                Path("other_dir/subdir/file2.py"),
            ],
        ),
        (
            (".cache|other.*subdir",),
            [
                Path("dir/subdir/file1.py"),
                Path("dir/subdir/file2.py"),
                Path("dir/subdir/file3.py"),
            ],
        ),
        (
            (".*/subdir/",),
            [
                Path(".cache/file1.py"),
                Path(".cache/file2.py"),
            ],
        ),
    ],
)
def test_regex_argument(exclude: tuple[str], expected: list[Path], tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        create_files([
            Path(".cache/file1.py"),
            Path(".cache/file2.py"),
            Path("dir/subdir/file1.py"),
            Path("dir/subdir/file2.py"),
            Path("dir/subdir/file3.py"),
            Path("other_dir/subdir/file1.py"),
            Path("other_dir/subdir/file2.py"),
        ])

        files = PythonFileFinder(
            exclude=exclude, extend_exclude=(), using_default_exclude=False
        ).get_all_python_files_in((Path(),))

        assert sorted(files) == expected


@pytest.mark.parametrize(
    ("exclude", "expected"),
    [
        (
            (".*file1",),
            [
                Path("dir/subdir/file2.py"),
                Path("dir/subdir/file3.py"),
                Path("other_dir/subdir/file2.py"),
            ],
        ),
        (
            (".*file1|.*file2",),
            [
                Path("dir/subdir/file3.py"),
            ],
        ),
        (
            (".*/subdir/",),
            [],
        ),
    ],
)
def test_multiple_source_directories(exclude: tuple[str], expected: list[Path], tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        create_files([
            Path("dir/subdir/file1.py"),
            Path("dir/subdir/file2.py"),
            Path("dir/subdir/file3.py"),
            Path("other_dir/subdir/file1.py"),
            Path("other_dir/subdir/file2.py"),
            Path("another_dir/subdir/file1.py"),
        ])

        files = PythonFileFinder(
            exclude=exclude, extend_exclude=(), using_default_exclude=False
        ).get_all_python_files_in((Path("dir"), Path("other_dir")))

        assert sorted(files) == expected


def test_duplicates_are_removed(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        create_files([Path("dir/subdir/file1.py")])

        files = PythonFileFinder(exclude=(), extend_exclude=(), using_default_exclude=False).get_all_python_files_in((
            Path(),
            Path(),
        ))

        assert sorted(files) == [Path("dir/subdir/file1.py")]


def test__generate_gitignore_pathspec_with_non_default_exclude(tmp_path: Path) -> None:
    gitignore_pathspec = PythonFileFinder(
        exclude=(), extend_exclude=(), using_default_exclude=False
    )._generate_gitignore_pathspec(Path())

    assert gitignore_pathspec is None


def test__generate_gitignore_pathspec_with_non_existing_gitignore(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        gitignore_pathspec = PythonFileFinder(
            exclude=(), extend_exclude=(), using_default_exclude=True
        )._generate_gitignore_pathspec(Path())

        assert gitignore_pathspec is None


def test__generate_gitignore_pathspec_with_existing_gitignore(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        with Path(".gitignore").open("w") as gitignore:
            gitignore.write("foo.py\nbar/")

        gitignore_pathspec = PythonFileFinder(
            exclude=(), extend_exclude=(), using_default_exclude=True
        )._generate_gitignore_pathspec(Path())

        assert isinstance(gitignore_pathspec, PathSpec)
        assert gitignore_pathspec.patterns == [
            GitWildMatchPattern("foo.py"),
            GitWildMatchPattern("bar/"),
        ]
