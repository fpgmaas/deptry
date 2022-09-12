import pytest

from deptry.result_logger import ResultLogger


def test_simple():
    issues = {
        "missing": ["foo"],
        "obsolete": ["foo"],
        "transitive": ["foo"],
        "misplaced_dev": ["foo"],
    }
    with pytest.raises(SystemExit) as e:
        ResultLogger(issues).log_and_exit()

    assert e.type == SystemExit
    assert e.value.code == 1


def test_no_issues():
    issues = {}
    with pytest.raises(SystemExit) as e:
        ResultLogger(issues).log_and_exit()

    assert e.type == SystemExit
    assert e.value.code == 0
