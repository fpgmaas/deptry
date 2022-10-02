import logging
import sys
from pathlib import Path
from typing import List, Optional, Tuple, Union

import click

from deptry.cli_defaults import DEFAULTS
from deptry.compat import metadata
from deptry.config import read_configuration_from_pyproject_toml
from deptry.core import Core
from deptry.utils import PYPROJECT_TOML_PATH, run_within_dir


class CommaSeparatedTupleParamType(click.ParamType):
    name = "tuple"

    def convert(
        self,
        value: Union[str, List[str], Tuple[str, ...]],
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> Tuple[str, ...]:
        if isinstance(value, str):
            return tuple(value.split(","))
        if isinstance(value, list):
            return tuple(value)
        return value


COMMA_SEPARATED_TUPLE = CommaSeparatedTupleParamType()


def configure_logger(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    log_level = logging.DEBUG if value else logging.INFO
    logging.basicConfig(level=log_level, handlers=[logging.StreamHandler()], format="%(message)s")


@click.command()
@click.argument("root", type=click.Path(exists=True, path_type=Path), required=False)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help=(
        "Boolean flag for verbosity. Using this flag will display more information about files, imports and"
        " dependencies while running."
    ),
    is_eager=True,
    callback=configure_logger,
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
    help=(
        "Boolean flag to specify if deptry should skip scanning the project for development dependencies that should be"
        " regular dependencies."
    ),
)
@click.option(
    "--ignore-obsolete",
    "-io",
    type=COMMA_SEPARATED_TUPLE,
    help="""
    Comma-separated list of dependencies that should never be marked as obsolete, even if they are not imported in any of the files scanned.
    For example; `deptry . --ignore-obsolete foo,bar`.
    """,
    default=DEFAULTS["ignore_obsolete"],
)
@click.option(
    "--ignore-missing",
    "-im",
    type=COMMA_SEPARATED_TUPLE,
    help="""Comma-separated list of modules that should never be marked as missing dependencies, even if the matching package for the import statement cannot be found.
    For example; `deptry . --ignore-missing foo,bar`.
    """,
    default=DEFAULTS["ignore_missing"],
)
@click.option(
    "--ignore-transitive",
    "-it",
    type=COMMA_SEPARATED_TUPLE,
    help="""Comma-separated list of dependencies that should never be marked as an issue due to it being a transitive dependency, even though deptry determines them to be transitive.
    For example; `deptry . --ignore-transitive foo,bar`.
    """,
    default=DEFAULTS["ignore_transitive"],
)
@click.option(
    "--ignore-misplaced-dev",
    "-id",
    type=COMMA_SEPARATED_TUPLE,
    help="""Comma-separated list of modules that should never be marked as a misplaced development dependency, even though it seems to not be used solely for development purposes.
    For example; `deptry . --ignore-misplaced-dev foo,bar`.
    """,
    default=DEFAULTS["ignore_misplaced_dev"],
)
@click.option(
    "--exclude",
    "-e",
    multiple=True,
    type=click.STRING,
    help="""A regular expression for directories or files in which .py files should not be scanned for imports to determine if there are dependency issues.
    Can be used multiple times by specifying the argument multiple times. re.match() is used to match the expressions, which by default checks for a match only at the beginning of a string.
    For example: `deptry . -e ".*/foo/" -e bar"` Note that this overwrites the defaults.
    """,
    default=DEFAULTS["exclude"],
    show_default=True,
)
@click.option(
    "--extend-exclude",
    "-ee",
    type=click.STRING,
    multiple=True,
    help="""Like --exclude, but adds additional files and directories on top of the excluded ones instead of overwriting the defaults.
    (Useful if you simply want to add to the default) `deptry . -ee ".*/foo/" -ee bar"`""",
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
    type=COMMA_SEPARATED_TUPLE,
    help=""".txt files to scan for dependencies. If a file called pyproject.toml with a [tool.poetry.dependencies] section is found, this argument is ignored
    and the dependencies are extracted from the pyproject.toml file instead. Can be multiple e.g. `deptry . --requirements-txt req/prod.txt,req/extra.txt`""",
    default=DEFAULTS["requirements_txt"],
    show_default=True,
)
@click.option(
    "--requirements-txt-dev",
    "-rtd",
    type=COMMA_SEPARATED_TUPLE,
    help=""".txt files to scan for additional development dependencies. If a file called pyproject.toml with a [tool.poetry.dependencies] section is found, this argument is ignored
    and the dependencies are extracted from the pyproject.toml file instead. Can be multiple e.g. `deptry . --requirements-txt-dev req/dev.txt,req/test.txt`""",
    default=DEFAULTS["requirements_txt_dev"],
    show_default=True,
)
@click.option(
    "--json-output",
    "-o",
    type=click.STRING,
    help="""If specified, a summary of the dependency issues found will be written to the output location specified. e.g. `deptry . -o deptry.json`""",
    default=DEFAULTS["json_output"],
    show_default=True,
)
@click.option(
    "--config",
    type=click.Path(),
    is_eager=True,
    callback=read_configuration_from_pyproject_toml,
    help="Path to the pyproject.toml file to read configuration from.",
    default=PYPROJECT_TOML_PATH,
    hidden=True,
)
def deptry(
    root: Optional[Path],
    verbose: bool,
    ignore_obsolete: Tuple[str, ...],
    ignore_missing: Tuple[str, ...],
    ignore_transitive: Tuple[str, ...],
    ignore_misplaced_dev: Tuple[str, ...],
    skip_obsolete: bool,
    skip_missing: bool,
    skip_transitive: bool,
    skip_misplaced_dev: bool,
    exclude: Tuple[str, ...],
    extend_exclude: Tuple[str, ...],
    ignore_notebooks: bool,
    requirements_txt: Tuple[str, ...],
    requirements_txt_dev: Tuple[str, ...],
    json_output: str,
    version: bool,
    config: str,
) -> None:
    """Find dependency issues in your Python project.

    [ROOT] is the path to the root directory of the project to be scanned.
    All other arguments should be specified relative to [ROOT].

    """

    if version:
        display_deptry_version()
        sys.exit(0)

    if not root:
        logging.warning("Missing argument ROOT. E.g. `deptry .`")
        sys.exit(1)

    with run_within_dir(root):
        Core(
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
            json_output=json_output,
        ).run()


def display_deptry_version() -> None:
    logging.info(f'deptry {metadata.version("deptry")}')  # type: ignore[no-untyped-call]
