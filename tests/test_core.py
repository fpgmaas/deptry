import logging

import pytest

from deptry.core import Core


def test_simple():
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


def test_no_issues():
    issues = {}
    with pytest.raises(SystemExit) as e:
        Core._exit(issues)

    assert e.type == SystemExit
    assert e.value.code == 0
