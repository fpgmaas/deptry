from __future__ import annotations

import pytest

from deptry.core import Core


def test_simple() -> None:
    issues = {
        "missing": ["foo"],
        "obsolete": ["foo"],
        "transitive": ["foo"],
        "misplaced_dev": ["foo"],
    }
    with pytest.raises(SystemExit) as e:
        Core._exit(issues)

    assert e.type == SystemExit
    assert e.value.code == 1


def test_no_issues() -> None:
    issues: dict[str, list[str]] = {}
    with pytest.raises(SystemExit) as e:
        Core._exit(issues)

    assert e.type == SystemExit
    assert e.value.code == 0
