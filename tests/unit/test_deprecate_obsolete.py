from __future__ import annotations

import pytest

from deptry.deprecate_obsolete import (
    IGNORE_OBSOLETE_AND_IGNORE_UNUSED_ERROR_MESSAGE,
    IGNORE_OBSOLETE_WARNING,
    SKIP_OBSOLETE_AND_SKIP_UNUSED_ERROR_MESSAGE,
    SKIP_OBSOLETE_WARNING,
    get_value_for_ignore_unused,
    get_value_for_skip_unused,
)


def test_skip_obsolete(caplog):
    result = get_value_for_skip_unused(skip_obsolete=True, skip_unused=False)
    assert result
    assert SKIP_OBSOLETE_WARNING in caplog.text


def test_skip_unused():
    result = get_value_for_skip_unused(skip_obsolete=False, skip_unused=True)
    assert result


def test_skip_unused_and_skip_obsolete():
    with pytest.raises(ValueError) as exc_info:
        get_value_for_skip_unused(skip_obsolete=True, skip_unused=True)
    assert str(exc_info.value) == SKIP_OBSOLETE_AND_SKIP_UNUSED_ERROR_MESSAGE


def test_ignore_obsolete(caplog):
    result = get_value_for_ignore_unused(ignore_obsolete="a", ignore_unused=None)
    assert result == "a"
    assert IGNORE_OBSOLETE_WARNING in caplog.text


def test_ignore_unused():
    result = get_value_for_ignore_unused(ignore_obsolete=None, ignore_unused="a")
    assert result == "a"


def test_ignore_unused_and_ignore_obsolete():
    with pytest.raises(ValueError) as exc_info:
        get_value_for_ignore_unused(ignore_obsolete="b", ignore_unused="a")
    assert str(exc_info.value) == IGNORE_OBSOLETE_AND_IGNORE_UNUSED_ERROR_MESSAGE
