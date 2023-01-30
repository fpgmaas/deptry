from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from deptry.utils import load_pyproject_toml

if TYPE_CHECKING:
    from pathlib import Path

    import click


def read_configuration_from_pyproject_toml(ctx: click.Context, _param: click.Parameter, value: Path) -> Path | None:
    """
    Callback that, given a click context, overrides the default values with configuration options set in a
    pyproject.toml file.
    Using a callback ensures that the following order is respected for setting an option:
    1. Default value is set
    2. Value is overrode by the one set from pyproject.toml, if any
    3. Value is overrode by the one set from the command line, if any
    """

    try:
        pyproject_data = load_pyproject_toml(value)
    except FileNotFoundError:
        logging.debug("No pyproject.toml file to read configuration from.")
        return value

    try:
        deptry_toml_config = pyproject_data["tool"]["deptry"]
    except KeyError:
        logging.debug("No configuration for deptry was found in pyproject.toml.")
        return value

    click_default_map: dict[str, Any] = {}

    if ctx.default_map:
        click_default_map.update(ctx.default_map)

    click_default_map.update(deptry_toml_config)

    ctx.default_map = click_default_map

    return value
