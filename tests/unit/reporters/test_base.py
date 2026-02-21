from __future__ import annotations

import sys
from pathlib import Path

import pytest

from deptry.reporters import TextReporter


@pytest.mark.skipif(sys.platform == "win32", reason="Explicitly tests paths output for non-Windows systems")
def test__format_path_non_windows() -> None:
    reporter = TextReporter([], enforce_posix_paths=False)

    assert reporter._format_path(Path("src/main.py")) == "src/main.py"


@pytest.mark.skipif(sys.platform != "win32", reason="Explicitly tests paths output for Windows systems")
def test__format_path_windows() -> None:
    reporter = TextReporter([], enforce_posix_paths=False)

    assert reporter._format_path(Path("src/main.py")) == "src\\main.py"


@pytest.mark.skipif(sys.platform == "win32", reason="Explicitly tests paths output for non-Windows systems")
def test__format_path_enforce_posix_paths_non_windows() -> None:
    reporter = TextReporter([], enforce_posix_paths=True)

    assert reporter._format_path(Path("src/main.py")) == "src/main.py"


@pytest.mark.skipif(sys.platform != "win32", reason="Explicitly tests paths output for Windows systems")
def test__format_path_enforce_posix_paths_windows() -> None:
    reporter = TextReporter([], enforce_posix_paths=True)

    assert reporter._format_path(Path("src/main.py")) == "src/main.py"
