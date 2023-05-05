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

        for issue_type, issues in self.issues.items():
            output[issue_type] = [
                (
                    issue.issue.package
                    if isinstance(issue.issue, Module) and issue.issue_type is TransitiveDependenciesFinder
                    else issue.issue.name
                )
                for issue in issues
            ]

        with open(self.json_output, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
