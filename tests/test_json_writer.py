import json
from pathlib import Path

from deptry.json_writer import JsonWriter
from deptry.utils import run_within_dir


def test_simple(tmp_path: Path) -> None:
    with run_within_dir(tmp_path):
        JsonWriter(json_output="output.json").write(issues={"one": ["two"], "three": ["four"]})

        with open("output.json") as f:
            data = json.load(f)

        assert data["one"] == ["two"]
        assert data["three"] == ["four"]
