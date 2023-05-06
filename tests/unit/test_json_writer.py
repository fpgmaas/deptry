from __future__ import annotations

import json
from typing import TYPE_CHECKING

from deptry.json_writer import JsonWriter
from tests.utils import run_within_dir

if TYPE_CHECKING:
    from pathlib import Path


def test_simple(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        JsonWriter(json_output="output.json").write(issues={"one": ["two"], "three": ["four"]})

        with open("output.json") as f:
            data = json.load(f)

        assert data["one"] == ["two"]
        assert data["three"] == ["four"]
