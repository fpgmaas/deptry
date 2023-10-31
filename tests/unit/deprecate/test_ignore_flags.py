from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from deptry.deprecate.ignore_flags import generate_deprecation_warning, get_value_for_per_rule_ignores_argument

if TYPE_CHECKING:
    from collections.abc import MutableMapping


def test_generate_deprecation_warning() -> None:
    result = generate_deprecation_warning(flag_name="ignore-missing", issue_code="DEP002", sequence=("hi", "bye"))
    assert (
        result == "Warning: In an upcoming release, support for the `--ignore-missing` command-line option and the"
        " `ignore_missing` configuration parameter will be discontinued. Instead, use `--per-rule-ignores"
        ' DEP002=hi|bye` or add a line `DEP002 = ["hi", "bye"]` to the `[tool.deptry.per_rule_ignores]` section of the'
        " configuration file."
    )


@pytest.mark.parametrize(
    ("ignore_params", "expected_result", "flag_name", "issue_code"),
    [
        (
            {
                "ignore_obsolete": (),
                "ignore_unused": (),
                "ignore_missing": ("hello", "goodbye"),
                "ignore_transitive": (),
                "ignore_misplaced_dev": (),
            },
            {"DEP001": ("hello", "goodbye")},
            "ignore-missing",
            "DEP001",
        ),
        (
            {
                "ignore_obsolete": ("hello", "goodbye"),
                "ignore_unused": (),
                "ignore_missing": (),
                "ignore_transitive": (),
                "ignore_misplaced_dev": (),
            },
            {"DEP002": ("hello", "goodbye")},
            "ignore-obsolete",
            "DEP002",
        ),
        (
            {
                "ignore_obsolete": (),
                "ignore_unused": ("hello", "goodbye"),
                "ignore_missing": (),
                "ignore_transitive": (),
                "ignore_misplaced_dev": (),
            },
            {"DEP002": ("hello", "goodbye")},
            "ignore-unused",
            "DEP002",
        ),
        (
            {
                "ignore_obsolete": (),
                "ignore_unused": (),
                "ignore_missing": (),
                "ignore_transitive": ("hello", "goodbye"),
                "ignore_misplaced_dev": (),
            },
            {"DEP003": ("hello", "goodbye")},
            "ignore-transitive",
            "DEP003",
        ),
        (
            {
                "ignore_obsolete": (),
                "ignore_unused": (),
                "ignore_missing": (),
                "ignore_transitive": (),
                "ignore_misplaced_dev": ("hello", "goodbye"),
            },
            {"DEP004": ("hello", "goodbye")},
            "ignore-misplaced-dev",
            "DEP004",
        ),
    ],
)
def test_ignore_param(
    caplog: pytest.LogCaptureFixture,
    ignore_params: MutableMapping[str, tuple[str, ...]],
    expected_result: MutableMapping[str, tuple[str, ...]],
    flag_name: str,
    issue_code: str,
) -> None:
    result = get_value_for_per_rule_ignores_argument(per_rule_ignores={}, **ignore_params)
    assert result == expected_result
    assert (
        generate_deprecation_warning(flag_name=flag_name, issue_code=issue_code, sequence=("hello", "goodbye"))
        in caplog.text
    )


@pytest.mark.parametrize(
    ("ignore_params", "expected_result", "flag_name", "issue_code"),
    [
        (
            {
                "ignore_obsolete": (),
                "ignore_unused": (),
                "ignore_missing": ("hello", "goodbye"),
                "ignore_transitive": (),
                "ignore_misplaced_dev": (),
            },
            {"DEP001": ("goodbye", "hello", "package")},
            "ignore-missing",
            "DEP001",
        ),
        (
            {
                "ignore_obsolete": ("hello", "goodbye"),
                "ignore_unused": (),
                "ignore_missing": (),
                "ignore_transitive": (),
                "ignore_misplaced_dev": (),
            },
            {"DEP002": ("goodbye", "hello", "package")},
            "ignore-obsolete",
            "DEP002",
        ),
        (
            {
                "ignore_obsolete": (),
                "ignore_unused": ("hello", "goodbye"),
                "ignore_missing": (),
                "ignore_transitive": (),
                "ignore_misplaced_dev": (),
            },
            {"DEP002": ("goodbye", "hello", "package")},
            "ignore-unused",
            "DEP002",
        ),
        (
            {
                "ignore_obsolete": (),
                "ignore_unused": (),
                "ignore_missing": (),
                "ignore_transitive": ("hello", "goodbye"),
                "ignore_misplaced_dev": (),
            },
            {"DEP003": ("goodbye", "hello", "package")},
            "ignore-transitive",
            "DEP003",
        ),
        (
            {
                "ignore_obsolete": (),
                "ignore_unused": (),
                "ignore_missing": (),
                "ignore_transitive": (),
                "ignore_misplaced_dev": ("hello", "goodbye"),
            },
            {"DEP004": ("goodbye", "hello", "package")},
            "ignore-misplaced-dev",
            "DEP004",
        ),
    ],
)
def test_ignore_param_append(
    caplog: pytest.LogCaptureFixture,
    ignore_params: MutableMapping[str, tuple[str, ...]],
    expected_result: MutableMapping[str, tuple[str, ...]],
    flag_name: str,
    issue_code: str,
) -> None:
    result = get_value_for_per_rule_ignores_argument(per_rule_ignores={issue_code: ("package",)}, **ignore_params)
    # We do not care about the order of the sequences that are in the values of the dict.
    assert {k: sorted(v) for k, v in result.items()} == {k: sorted(v) for k, v in expected_result.items()}
    assert (
        generate_deprecation_warning(flag_name=flag_name, issue_code=issue_code, sequence=("hello", "goodbye"))
        in caplog.text
    )
