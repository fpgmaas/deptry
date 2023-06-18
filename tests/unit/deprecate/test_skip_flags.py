from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest

from deptry.deprecate.skip_flags import generate_deprecation_warning, get_value_for_ignore_argument


def test_generate_deprecation_warning() -> None:
    result = generate_deprecation_warning(flag_name="skip-unused", issue_code="DEP002")
    assert (
        result
        == "Warning: In an upcoming release, support for the `--skip-unused` command-line option and the `skip_unused`"
        " configuration parameter will be discontinued. Instead, use `--ignore DEP002` or add a line `ignore ="
        " ['DEP002']` to the `[tool.deptry]` section of the configuration file."
    )


def test_skip_obsolete(caplog: pytest.LogCaptureFixture) -> None:
    result = get_value_for_ignore_argument(
        ignore=(),
        skip_obsolete=True,
        skip_unused=False,
        skip_missing=False,
        skip_transitive=False,
        skip_misplaced_dev=False,
    )
    assert result == ("DEP002",)
    assert generate_deprecation_warning(flag_name="skip-obsolete", issue_code="DEP002") in caplog.text


def test_skip_unused(caplog: pytest.LogCaptureFixture) -> None:
    result = get_value_for_ignore_argument(
        ignore=(),
        skip_obsolete=True,
        skip_unused=True,
        skip_missing=False,
        skip_transitive=False,
        skip_misplaced_dev=False,
    )
    assert result == ("DEP002",)
    assert generate_deprecation_warning(flag_name="skip-unused", issue_code="DEP002") in caplog.text


def test_skip_transitive_and_missing(caplog: pytest.LogCaptureFixture) -> None:
    result = get_value_for_ignore_argument(
        ignore=(),
        skip_obsolete=False,
        skip_unused=False,
        skip_missing=True,
        skip_transitive=True,
        skip_misplaced_dev=False,
    )
    assert result == ("DEP001", "DEP003")
    assert generate_deprecation_warning(flag_name="skip-missing", issue_code="DEP001") in caplog.text
    assert generate_deprecation_warning(flag_name="skip-transitive", issue_code="DEP003") in caplog.text
