from __future__ import annotations

import json
from dataclasses import dataclass

from deptry.issues_finder.transitive import TransitiveDependenciesFinder
from deptry.module import Module
from deptry.reporters.base import Reporter


@dataclass
class JSONReporter(Reporter):
    json_output: str

    def report(self) -> None:
        output = {}

        for issue_type, violations in self.violations.items():
            output[issue_type] = [
                (
                    violation.issue.package
                    if isinstance(violation.issue, Module) and violation.issue_type is TransitiveDependenciesFinder
                    else violation.issue.name
                )
                for violation in violations
            ]

        with open(self.json_output, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
