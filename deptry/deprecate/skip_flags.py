from __future__ import annotations

import logging

from deptry.violations import (
    DEP001MissingDependencyViolation,
    DEP002UnusedDependencyViolation,
    DEP003TransitiveDependencyViolation,
    DEP004MisplacedDevDependencyViolation,
)


def generate_deprecation_warning(flag_name: str, issue_code: str) -> str:
    return (
        f"Warning: In an upcoming release, support for the `--{flag_name}` command-line option and the"
        f" `{flag_name.replace('-', '_')}` configuration parameter will be discontinued. Instead, use `--ignore"
        f" {issue_code}` or add a line `ignore = ['{issue_code}']` to the `[tool.deptry]` section of the configuration"
        " file."
    )


def get_value_for_ignore_argument(
    ignore: tuple[str, ...],
    skip_obsolete: bool,
    skip_unused: bool,
    skip_missing: bool,
    skip_transitive: bool,
    skip_misplaced_dev: bool,
) -> tuple[str, ...]:
    """
    This function is designed to help with the transition from deprecated command-line flags to the new `--ignore` flag.
    The deprecated flags that are replaced by this new flag are:

        - `--skip-obsolete`
        - `--skip-unused`
        - `--skip-missing`
        - `--skip-transitive`
        - `--skip-misplaced-dev`

    This function accepts the values for the deprecated flags and updates the `ignore` parameter accordingly.

    Raise a warning if one of the to-be-deprecated flags is used.
    """
    user_values = {
        "skip-missing": skip_missing,
        "skip-unused": skip_unused,
        "skip-obsolete": skip_obsolete,
        "skip-transitive": skip_transitive,
        "skip-misplaced-dev": skip_misplaced_dev,
    }

    issue_codes = {
        "skip-missing": DEP001MissingDependencyViolation.error_code,
        "skip-unused": DEP002UnusedDependencyViolation.error_code,
        "skip-obsolete": DEP002UnusedDependencyViolation.error_code,
        "skip-transitive": DEP003TransitiveDependencyViolation.error_code,
        "skip-misplaced-dev": DEP004MisplacedDevDependencyViolation.error_code,
    }

    for flag, should_skip in user_values.items():
        if should_skip:
            code = issue_codes[flag]
            logging.warning(generate_deprecation_warning(flag, code))
            if code not in ignore:
                ignore += (code,)

    return ignore
