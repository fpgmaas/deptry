import logging
import pathlib
import sys
from typing import List

import click

from deptry.config import Config
from deptry.core import Core
from deptry.utils import run_within_dir


@click.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Boolean flag for verbosity. Using this flag will display more information about files, imports and dependencies while running.",
)
@click.option(
    "--ignore-dependencies",
    "-i",
    multiple=True,
    help="Dependencies listed in pyproject.toml that should be ignored, even if they are not imported.",
)
@click.option(
    "--ignore-directories",
    "-id",
    multiple=True,
    help="""Directories in which .py files should not be scanned for imports to determine if a dependency is used or not.
    Defaults to 'venv'. Specify multiple directories by using this flag twice, e.g. `-id .venv -id other_dir`""",
)
@click.option(
    "--ignore-notebooks",
    "-nb",
    is_flag=True,
    help="Boolean flag to specify if notebooks should be ignored while scanning for imports.",
)
def deptry(
    directory: pathlib.Path,
    verbose: bool,
    ignore_dependencies: List[str],
    ignore_directories: List[str],
    ignore_notebooks: bool,
) -> None:

    with run_within_dir(directory):
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(level=log_level, handlers=[logging.StreamHandler()], format="%(message)s")

        # Pass the CLI arguments to Config, if they are provided, otherwise pass 'None'.
        # This way, we can distinguish if a argument was actually passed by the user
        # (e.g. ignore_notebooks is 'False' by default).
        config = Config(
            ignore_dependencies=ignore_dependencies if ignore_dependencies else None,
            ignore_directories=ignore_directories if ignore_directories else None,
            ignore_notebooks=ignore_notebooks if ignore_notebooks else None,
        )

        obsolete_dependencies = Core(
            ignore_dependencies=config.ignore_dependencies,
            ignore_directories=config.ignore_directories,
            ignore_notebooks=config.ignore_notebooks,
        ).run()
        if len(obsolete_dependencies):
            logging.info(f"pyproject.toml contains obsolete dependencies: {obsolete_dependencies}")
            sys.exit(1)
        else:
            logging.info("Succes! No obsolete dependencies found.")
            sys.exit(0)
