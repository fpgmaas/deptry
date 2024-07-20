from __future__ import annotations

import operator
from typing import TYPE_CHECKING

from deptry.violations import (
    DEP001MissingDependenciesFinder,
    DEP002UnusedDependenciesFinder,
    DEP003TransitiveDependenciesFinder,
    DEP004MisplacedDevDependenciesFinder,
    DEP005StandardLibraryDependenciesFinder,
)

if TYPE_CHECKING:
    from typing import Mapping

    from deptry.dependency import Dependency
    from deptry.module import ModuleLocations
    from deptry.violations import Violation, ViolationsFinder


_VIOLATIONS_FINDERS: tuple[type[ViolationsFinder], ...] = (
    DEP001MissingDependenciesFinder,
    DEP002UnusedDependenciesFinder,
    DEP003TransitiveDependenciesFinder,
    DEP004MisplacedDevDependenciesFinder,
    DEP005StandardLibraryDependenciesFinder,
)


def find_violations(
    imported_modules_with_locations: list[ModuleLocations],
    dependencies: list[Dependency],
    ignore: tuple[str, ...],
    per_rule_ignores: Mapping[str, tuple[str, ...]],
    standard_library_modules: frozenset[str],
) -> list[Violation]:
    violations = []

    for violation_finder in _VIOLATIONS_FINDERS:
        if violation_finder.violation.error_code not in ignore:
            violations.extend(
                violation_finder(
                    imported_modules_with_locations=imported_modules_with_locations,
                    dependencies=dependencies,
                    ignored_modules=per_rule_ignores.get(violation_finder.violation.error_code, ()),
                    standard_library_modules=standard_library_modules,
                ).find()
            )
    return _get_sorted_violations(violations)


def _get_sorted_violations(violations: list[Violation]) -> list[Violation]:
    return sorted(
        violations, key=operator.attrgetter("location.file", "location.line", "location.column", "error_code")
    )
