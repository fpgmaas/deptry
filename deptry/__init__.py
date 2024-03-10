from __future__ import annotations

import logging

# //TODO: Remove this, and see if we can move the function to a submodule.
# Required to make `from deptry import get_imports_from_py_file` work.
from .deptry import *  # noqa: F403

logging.getLogger("nbconvert").setLevel(logging.WARNING)
