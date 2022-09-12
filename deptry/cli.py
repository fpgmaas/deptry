import logging
import pathlib
import sys
from typing import List

import click

from deptry.cli_defaults import DEFAULTS
from deptry.config import Config
from deptry.core import Core
from deptry.utils import import_importlib_metadata, run_within_dir


@click.command()
@click.argument("directory", type=click.Path(exists=True), required=False)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Boolean flag for verbosity. Using this flag will display more information about files, imports and dependencies while running.",
)
@click.option(
    "--skip-obsolete",
    is_flag=True,
    help="Boolean flag to specify if deptry should skip scanning the project for obsolete dependencies.",
)
@click.option(
    "--skip-missing",
    is_flag=True,
    help="Boolean flag to specify if deptry should skip scanning the project for missing dependencies.",
)
@click.option(
    "--skip-transitive",
    is_flag=True,
    help="Boolean flag to specify if deptry should skip scanning the project for transitive dependencies.",
)
@click.option(
    "--skip-misplaced-dev",
    is_flag=True,
    help="Boolean flag to specify if deptry should skip scanning the project for development dependencies that should be regular dependencies.",
)
@click.option(
    "--ignore-obsolete",
    "-io",
    type=click.STRING,
    help="""
    Comma-separated list of dependencies that should never be marked as obsolete, even if they are not imported in any of the files scanned.
    For example; `deptry . --ignore-obsolete foo,bar`.
    """,
    default=DEFAULTS["ignore_obsolete"],
)
@click.option(
    "--ignore-missing",
    "-im",
    type=click.STRING,
    help="""Comma-separated list of modules that should never be marked as missing dependencies, even if the matching package for the import statement cannot be found.
    For example; `deptry . --ignore-missing foo,bar`.
    """,
    default=DEFAULTS["ignore_missing"],
)
@click.option(
    "--ignore-transitive",
    "-it",
    type=click.STRING,
    help="""Comma-separated list of dependencies that should never be marked as an issue due to it being a transitive dependency, even though deptry determines them to be transitive.
    For example; `deptry . --ignore-transitive foo,bar`.
    """,
    default=DEFAULTS["ignore_transitive"],
)
@click.option(
    "--ignore-misplaced-dev",
    "-id",
    type=click.STRING,
    help="""Comma-separated list of modules that should never be marked as a misplaced development dependency, even though it seems to not be used solely for development purposes.
    For example; `deptry . --ignore-misplaced-dev foo,bar`.
    """,
    default=DEFAULTS["ignore_misplaced_dev"],
)
@click.option(
    "--exclude",
    "-e",
    type=click.STRING,
    help="""Comma-separated list of directories or files in which .py files should not be scanned for imports to determine if there are dependency issues.
    For example: `deptry . --exclude venv,.venv,tests,setup.py,foo,bar.py`
    """,
    default=DEFAULTS["exclude"],
    show_default=True,
)
@click.option(
    "--extend-exclude",
    "-ee",
    type=click.STRING,
    help="""Like --exclude, but adds additional files and directories on top of the excluded ones instead of overwriting the defaults.
    (Useful if you simply want to add to the default) `deptry . --extend-exclude foo,bar.py`""",
    default=DEFAULTS["extend_exclude"],
    show_default=True,
)
@click.option(
    "--ignore-notebooks",
    "-nb",
    is_flag=True,
    help="Boolean flag to specify if notebooks should be ignored while scanning for imports.",
)
@click.option(
    "--version",
    is_flag=True,
    help="Display the current version and exit.",
)
@click.option(
    "--requirements-txt",
    "-rt",
    type=click.STRING,
    help="""A .txt files with the project's dependencies. If a file called pyproject.toml with a [tool.poetry.dependencies] section is found, this argument is ignored
    and the dependencies are extracted from the pyproject.toml file instead. Example use: `deptry . --requirements-txt req/prod.txt`""",
    default=DEFAULTS["requirements_txt"],
    show_default=True,
)
@click.option(
    "--requirements-txt-dev",
    "-rtd",
    type=click.STRING,
    help=""".txt files to scan for additional development dependencies. If a file called pyproject.toml with a [tool.poetry.dependencies] section is found, this argument is ignored
    and the dependencies are extracted from the pyproject.toml file instead. Can be multiple e.g. `deptry . --requirements-txt-dev req/dev.txt,req/test.txt`""",
    default=DEFAULTS["requirements_txt_dev"],
    show_default=True,
)
def deptry(
    directory: pathlib.Path,
    verbose: bool,
    ignore_obsolete: List[str],
    ignore_missing: List[str],
    ignore_transitive: List[str],
    ignore_misplaced_dev: List[str],
    skip_obsolete: bool,
    skip_missing: bool,
    skip_transitive: bool,
    skip_misplaced_dev: bool,
    exclude: List[str],
    extend_exclude: List[str],
    ignore_notebooks: bool,
    requirements_txt: str,
    requirements_txt_dev: str,
    version: bool,
) -> None:
    """Find dependency issues in your Python project.

    [DIRECTORY] is the path to the root directory of the project to be scanned.
    All other arguments should be specified relative to [DIRECTORY].

    """

    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level, handlers=[logging.StreamHandler()], format="%(message)s")

    if version:
        display_deptry_version()
        sys.exit(0)

    if not directory:
        logging.warning("Missing argument directory. E.g. `deptry .`")
        sys.exit(1)

    with run_within_dir(directory):

        # Pass the CLI arguments to Config, if they are provided, otherwise pass 'None'.
        # This way, we can distinguish if a argument was actually passed by the user
        # (e.g. ignore_notebooks is 'False' by default).
        config = Config(
            ignore_obsolete=ignore_obsolete,
            ignore_missing=ignore_missing,
            ignore_transitive=ignore_transitive,
            ignore_misplaced_dev=ignore_misplaced_dev,
            exclude=exclude,
            extend_exclude=extend_exclude,
            ignore_notebooks=ignore_notebooks,
            skip_obsolete=skip_obsolete,
            skip_missing=skip_missing,
            skip_transitive=skip_transitive,
            skip_misplaced_dev=skip_misplaced_dev,
            requirements_txt=requirements_txt,
            requirements_txt_dev=requirements_txt_dev,
        )

        Core(
            ignore_obsolete=config.ignore_obsolete,
            ignore_missing=config.ignore_missing,
            ignore_transitive=config.ignore_transitive,
            ignore_misplaced_dev=config.ignore_misplaced_dev,
            exclude=config.exclude,
            extend_exclude=config.extend_exclude,
            ignore_notebooks=config.ignore_notebooks,
            skip_obsolete=config.skip_obsolete,
            skip_missing=config.skip_missing,
            skip_transitive=config.skip_transitive,
            skip_misplaced_dev=config.skip_misplaced_dev,
            requirements_txt=config.requirements_txt,
            requirements_txt_dev=config.requirements_txt_dev,
        ).run()


def display_deptry_version():
    metadata, *_ = import_importlib_metadata()
    logging.info(f'deptry {metadata.version("deptry")}')
