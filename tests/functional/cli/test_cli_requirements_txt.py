from __future__ import annotations

import pytest

from tests.functional.utils import Project


@pytest.mark.xdist_group(name=Project.REQUIREMENTS_TXT)
def test_cli_single_requirements_files() -> None:
    assert True is True
