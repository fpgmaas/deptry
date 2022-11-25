from __future__ import annotations

import json


class JsonWriter:
    """
    Class to write issues to a json file

    Args:
        json_output: file path to store output, e.g. `output.json`
    """

    def __init__(self, json_output: str) -> None:
        self.json_output = json_output

    def write(self, issues: dict[str, list[str]]) -> None:
        with open(self.json_output, "w", encoding="utf-8") as f:
            json.dump(issues, f, ensure_ascii=False, indent=4)
