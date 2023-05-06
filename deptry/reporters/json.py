from __future__ import annotations

import json
from dataclasses import dataclass

from deptry.reporters.base import Reporter


@dataclass
class JSONReporter(Reporter):
    json_output: str

    def report(self) -> None:
        with open(self.json_output, "w", encoding="utf-8") as f:
            json.dump(self.issues, f, ensure_ascii=False, indent=4)
