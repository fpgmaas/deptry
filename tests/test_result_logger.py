import logging

from deptry.result_logger import ResultLogger


def test_logging_number_multiple(caplog):
    with caplog.at_level(logging.INFO):
        issues = {
            "missing": ["foo"],
            "obsolete": ["foo"],
            "transitive": ["foo"],
            "misplaced_dev": ["foo"],
        }
        ResultLogger(issues).log_and_exit()
    assert "There were 4 dependency issues found" in caplog.text
    assert "The project contains obsolete dependencies" in caplog.text
    assert "There are dependencies missing from the project's list of dependencies" in caplog.text
    assert "There are transitive dependencies that should be explicitly defined as dependencies" in caplog.text
    assert "There are imported modules from development dependencies detected" in caplog.text
    assert "For more information, see the documentation" in caplog.text


def test_logging_number_single(caplog):
    with caplog.at_level(logging.INFO):
        issues = {
            "missing": ["foo"],
        }
        ResultLogger(issues).log_and_exit()
    assert "There was 1 dependency issue found" in caplog.text


def test_logging_number_none(caplog):
    with caplog.at_level(logging.INFO):
        issues = {
            "missing": [],
        }
        ResultLogger(issues).log_and_exit()
    assert "No dependency issues found" in caplog.text
    assert "There were 4 dependency issues found" not in caplog.text
    assert "The project contains obsolete dependencies" not in caplog.text
    assert "There are dependencies missing from the project's list of dependencies" not in caplog.text
    assert "There are transitive dependencies that should be explicitly defined as dependencies" not in caplog.text
    assert "There are imported modules from development dependencies detected" not in caplog.text
    assert "For more information, see the documentation" not in caplog.text
