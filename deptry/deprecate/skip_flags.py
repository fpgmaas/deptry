from __future__ import annotations

import logging


def generate_deprecation_warning(flag_name: str, issue_code: str) -> str:
    return (
        f"Warning: In an upcoming release, support for the `--{flag_name}` command-line option and the"
        f" `{flag_name.replace('-','_')}` configuration parameter will be discontinued. Instead, use `--ignore"
        f" {issue_code}` or `ignore = ['{issue_code}']`."
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
    Convert the to-be-deprecated CLI flags --skip-<type>, where type is e.g. unused, to the new CLI flag '--ignore'.
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
        "skip-missing": "DEP001",
        "skip-unused": "DEP002",
        "skip-obsolete": "DEP002",
        "skip-transitive": "DEP003",
        "skip-misplaced-dev": "DEP004",
    }

    for flag, should_skip in user_values.items():
        if should_skip:
            code = issue_codes[flag]
            logging.warning(generate_deprecation_warning(flag, code))
            if code not in ignore:
                ignore += (code,)

    return ignore
