from __future__ import annotations

from pathlib import Path

from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern

from deptry.python_file_finder import PythonFileFinder
from tests.utils import create_files_from_list_of_dicts, run_within_dir


def test_simple(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        paths = [
            {"dir": "dir/subdir", "file": "file1.py"},
            {"dir": "dir/subdir", "file": "file2.py"},
            {"dir": "dir/subdir", "file": "file3.py"},
            {"dir": "other_dir/subdir", "file": "file1.py"},
            {"dir": "other_dir/subdir", "file": "file2.py"},
        ]
        create_files_from_list_of_dicts(paths)

        files = PythonFileFinder(
            exclude=(".venv",), extend_exclude=("other_dir",), using_default_exclude=False
        ).get_all_python_files_in(Path("."))
        assert len(files) == 3
        assert "dir/subdir/file2.py" in [str(file) for file in files]


def test_only_matches_start(tmp_path: Path) -> None:
    """
    Test the adding 'subdir' as exclude argument does not also exclude dir/subdir.
    """
    with run_within_dir(tmp_path):
        paths = [
            {"dir": "dir/subdir", "file": "file1.py"},
            {"dir": "dir/subdir", "file": "file2.py"},
            {"dir": "dir/subdir", "file": "file3.py"},
            {"dir": "subdir", "file": "file1.py"},
            {"dir": "subdir", "file": "file2.py"},
        ]
        create_files_from_list_of_dicts(paths)

        files = PythonFileFinder(
            exclude=("subdir",), extend_exclude=(), using_default_exclude=False
        ).get_all_python_files_in(Path("."))
        assert len(files) == 3
        assert "dir/subdir/file2.py" in [str(file) for file in files]


def test_matches_ipynb(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        paths = [
            {"dir": "dir/subdir", "file": "file1.ipynb"},
        ]
        create_files_from_list_of_dicts(paths)

        files = PythonFileFinder(
            exclude=(), extend_exclude=(), using_default_exclude=False, ignore_notebooks=False
        ).get_all_python_files_in(Path("."))
        assert len(files) == 1
        assert "dir/subdir/file1.ipynb" in [str(file) for file in files]
        files = PythonFileFinder(
            exclude=(), extend_exclude=(), using_default_exclude=False, ignore_notebooks=True
        ).get_all_python_files_in(Path("."))
        assert len(files) == 0


def test_regex_argument(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        paths = [
            {"dir": "dir/subdir", "file": "file1.py"},
            {"dir": "dir/subdir", "file": "file2.py"},
            {"dir": "dir/subdir", "file": "file3.py"},
            {"dir": "other_dir/subdir", "file": "file1.py"},
            {"dir": "other_dir/subdir", "file": "file2.py"},
            {"dir": ".cache", "file": "file1.py"},
            {"dir": ".cache", "file": "file2.py"},
        ]
        create_files_from_list_of_dicts(paths)

        files = PythonFileFinder(
            exclude=(".*file1",), extend_exclude=(), using_default_exclude=False, ignore_notebooks=False
        ).get_all_python_files_in(Path("."))
        assert len(files) == 4
        assert not any("file1" in str(file) for file in files)

        files = PythonFileFinder(
            exclude=(".cache|other.*subdir",), extend_exclude=(), using_default_exclude=False, ignore_notebooks=False
        ).get_all_python_files_in(Path("."))
        assert len(files) == 3
        assert not any("other_dir" in str(file) for file in files)
        assert not any(".cache" in str(file) for file in files)
        assert "dir/subdir/file2.py" in [str(file) for file in files]

        files = PythonFileFinder(
            exclude=(".*/subdir/",), extend_exclude=(), using_default_exclude=False, ignore_notebooks=False
        ).get_all_python_files_in(Path("."))
        assert len(files) == 2
        assert not any("subdir" in str(file) for file in files)
        assert ".cache/file2.py" in [str(file) for file in files]


def test__generate_gitignore_pathspec_with_non_default_exclude(tmp_path: Path) -> None:
    gitignore_pathspec = PythonFileFinder(
        exclude=(), extend_exclude=(), using_default_exclude=False
    )._generate_gitignore_pathspec(Path("."))

    assert gitignore_pathspec is None


def test__generate_gitignore_pathspec_with_non_existing_gitignore(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        gitignore_pathspec = PythonFileFinder(
            exclude=(), extend_exclude=(), using_default_exclude=True
        )._generate_gitignore_pathspec(Path("."))

        assert gitignore_pathspec is None


def test__generate_gitignore_pathspec_with_existing_gitignore(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        with open(Path(".gitignore"), "w") as gitignore:
            gitignore.write("foo.py\nbar/")

        gitignore_pathspec = PythonFileFinder(
            exclude=(), extend_exclude=(), using_default_exclude=True
        )._generate_gitignore_pathspec(Path("."))

        assert isinstance(gitignore_pathspec, PathSpec)
        assert gitignore_pathspec.patterns == [
            GitWildMatchPattern("foo.py"),
            GitWildMatchPattern("bar/"),
        ]
