from __future__ import annotations

import json
from typing import TYPE_CHECKING

from deptry.reporters import JSONReporter
from tests.utils import run_within_dir

if TYPE_CHECKING:
    from pathlib import Path


def test_simple(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        JSONReporter({"one": ["two"], "three": ["four"]}, "output.json").report()

        with open("output.json") as f:
            data = json.load(f)

        assert data["one"] == ["two"]
        assert data["three"] == ["four"]
