from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import click


def handle_deprecations(ctx: click.Context) -> None:
    if ctx.params["pep621_dev_dependency_groups"] and ctx.params["optional_dependencies_dev_groups"]:
        logging.error(
            "Error: Cannot use both `--pep621-dev-dependency-groups` and `--optional-dependencies-dev-groups`. Only "
            "use the latter, as the former is deprecated."
        )
        ctx.exit(2)

    if ctx.params["pep621_dev_dependency_groups"]:
        logging.warning(
            "Warning: In an upcoming release, support for the `--pep621-dev-dependency-groups` command-line option "
            "and the `pep621_dev_dependency_groups` configuration parameter will be discontinued. Instead, use "
            "`--optional-dependencies-dev-groups` or `optional_dependencies_dev_groups` under the `[tool.deptry]` "
            "section in pyproject.toml."
        )
