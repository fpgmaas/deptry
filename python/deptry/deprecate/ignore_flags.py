from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from deptry.violations import (
    DEP001MissingDependencyViolation,
    DEP002UnusedDependencyViolation,
    DEP003TransitiveDependencyViolation,
    DEP004MisplacedDevDependencyViolation,
)

if TYPE_CHECKING:
    from collections.abc import MutableMapping


def generate_deprecation_warning(flag_name: str, issue_code: str, sequence: tuple[str, ...]) -> str:
    sequence_as_list_string = "[" + ", ".join(f'"{x}"' for x in sequence) + "]"
    return (
        f"Warning: In an upcoming release, support for the `--{flag_name}` command-line option and the"
        f" `{flag_name.replace('-', '_')}` configuration parameter will be discontinued. Instead, use"
        f" `--per-rule-ignores {issue_code}={'|'.join(sequence)}` or add a line `{issue_code} ="
        f" {sequence_as_list_string}` to the `[tool.deptry.per_rule_ignores]` section of the configuration file."
    )


def get_value_for_per_rule_ignores_argument(
    per_rule_ignores: MutableMapping[str, tuple[str, ...]],
    ignore_obsolete: tuple[str, ...],
    ignore_unused: tuple[str, ...],
    ignore_missing: tuple[str, ...],
    ignore_transitive: tuple[str, ...],
    ignore_misplaced_dev: tuple[str, ...],
) -> MutableMapping[str, tuple[str, ...]]:
    """
    This function is designed to help with the transition from deprecated command-line flags to the new `--per-rule-ignores` flag.
    The deprecated flags that are replaced by this new flag are:

        - `--ignore-obsolete`
        - `--ignore-unused`
        - `--ignore-missing`
        - `--ignore-transitive`
        - `--ignore-misplaced-dev`

    This function accepts the values for the deprecated flags and updates the `per_rule_ignores` mapping accordingly.

    Raise a warning if one of the to-be-deprecated flags is used.
    """
    user_values = {
        "ignore-missing": ignore_missing,
        "ignore-unused": ignore_unused,
        "ignore-obsolete": ignore_obsolete,
        "ignore-transitive": ignore_transitive,
        "ignore-misplaced-dev": ignore_misplaced_dev,
    }

    issue_codes = {
        "ignore-missing": DEP001MissingDependencyViolation.error_code,
        "ignore-unused": DEP002UnusedDependencyViolation.error_code,
        "ignore-obsolete": DEP002UnusedDependencyViolation.error_code,
        "ignore-transitive": DEP003TransitiveDependencyViolation.error_code,
        "ignore-misplaced-dev": DEP004MisplacedDevDependencyViolation.error_code,
    }

    for flag, modules_or_dependencies_to_be_ignored in user_values.items():
        if modules_or_dependencies_to_be_ignored:
            code = issue_codes[flag]
            logging.warning(generate_deprecation_warning(flag, code, modules_or_dependencies_to_be_ignored))
            if code not in per_rule_ignores:
                per_rule_ignores[code] = modules_or_dependencies_to_be_ignored
            else:
                per_rule_ignores[code] = tuple(set(per_rule_ignores[code]).union(modules_or_dependencies_to_be_ignored))

    return per_rule_ignores
