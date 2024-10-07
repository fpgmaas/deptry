from __future__ import annotations

import sys

# Although `importlib.metadata` is available before Python 3.11, we benefit from using `importlib_metadata` package
# on Python < 3.11 because it exposes `packages_distributions` function that we use in the codebase. Python 3.10 also
# has this function, but there are features we need in it that are only available in Python >= 3.11. So by using
# `importlib_metadata`, we benefit from those features for all Python versions we support.
if sys.version_info >= (3, 11):
    import importlib.metadata as importlib_metadata
else:
    import importlib_metadata  # pragma: no cover


__all__ = ("importlib_metadata",)
