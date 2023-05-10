from __future__ import annotations

import logging

SKIP_OBSOLETE_WARNING = (
    "Warning: In an upcoming release, support for the `--skip-obsolete` command-line option and the `skip_obsolete`"
    " configuration parameter will be discontinued. Instead, use the `--skip-unused` option or the `skip_unused`"
    " configuration parameter to achieve the desired behavior."
)
IGNORE_OBSOLETE_WARNING = (
    "Warning: In an upcoming release, support for the `--ignore-obsolete` command-line option and the `ignore_obsolete`"
    " configuration parameter will be discontinued. Instead, use the `--ignore-unused` option or the `ignore_unused`"
    " configuration parameter to achieve the desired behavior."
)
SKIP_OBSOLETE_AND_SKIP_UNUSED_ERROR_MESSAGE = (
    "Both `skip_obsolete` and `skip_unused` options are set, either in pyproject.toml or through their corresponding"
    " CLI arguments. Please use only the `skip_unused` option, as `skip_obsolete` will be deprecated in the future."
)
IGNORE_OBSOLETE_AND_IGNORE_UNUSED_ERROR_MESSAGE = (
    "Both `ignore_obsolete` and `ignore_unused` options are set, either in pyproject.toml or through their"
    " corresponding CLI arguments. Please use only the `ignore_unused` option, as `ignore_obsolete` will be deprecated"
    " in the future."
)


def get_value_for_skip_unused(skip_obsolete: bool, skip_unused: bool) -> bool:
    """
    The skip_obsolete argument will be deprecated in the future, users should use skip_unused instead.
    If only skip_obsolete is defined, display a warning message. If both skip_obsolete and skip_unused are defined,
    raise an Error.
    """
    if skip_obsolete:
        logging.warning(SKIP_OBSOLETE_WARNING)
        if skip_unused:
            raise ValueError(SKIP_OBSOLETE_AND_SKIP_UNUSED_ERROR_MESSAGE)
        else:
            return skip_obsolete
    return skip_unused


def get_value_for_ignore_unused(ignore_obsolete: tuple[str, ...], ignore_unused: tuple[str, ...]) -> tuple[str, ...]:
    """
    The ignore_obsolete argument will be deprecated in the future, users should use ignore_unused instead.
    If only ignore_obsolete is defined, display a warning message. If both ignore_obsolete and ignore_unused are defined,
    raise an Error.
    """
    if ignore_obsolete:
        logging.warning(IGNORE_OBSOLETE_WARNING)
        if ignore_unused:
            raise ValueError(IGNORE_OBSOLETE_AND_IGNORE_UNUSED_ERROR_MESSAGE)
        else:
            return ignore_obsolete
    return ignore_unused
