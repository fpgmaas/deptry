from __future__ import annotations

import logging
from pathlib import Path

import click

from deptry.compat import metadata
from deptry.config import read_configuration_from_pyproject_toml
from deptry.core import Core


class CommaSeparatedTupleParamType(click.ParamType):
    name = "tuple"

    def convert(
        self,
        value: str | list[str] | tuple[str, ...],
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> tuple[str, ...]:
        if isinstance(value, str):
            return tuple(value.split(","))
        if isinstance(value, list):
            return tuple(value)
        return value


COMMA_SEPARATED_TUPLE = CommaSeparatedTupleParamType()


def configure_logger(_ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    log_level = logging.DEBUG if value else logging.INFO
    logging.basicConfig(level=log_level, handlers=[logging.StreamHandler()], format="%(message)s")


def display_deptry_version(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    if not value or ctx.resilient_parsing:
        return None

    click.echo(f'deptry {metadata.version("deptry")}')  # type: ignore[no-untyped-call]
    ctx.exit()


@click.command()
@click.argument("root", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help=(
        "Boolean flag for verbosity. Using this flag will display more information about files, imports and"
        " dependencies while running."
    ),
    expose_value=False,
    is_eager=True,
    callback=configure_logger,
)
@click.option(
    "--config",
    type=click.Path(path_type=Path),
    is_eager=True,
    callback=read_configuration_from_pyproject_toml,
    help="Path to the pyproject.toml file to read configuration from.",
    default="pyproject.toml",
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
    default=(),
)
@click.option(
    "--ignore-missing",
    "-im",
    type=COMMA_SEPARATED_TUPLE,
    help="""Comma-separated list of modules that should never be marked as missing dependencies, even if the matching package for the import statement cannot be found.
    For example; `deptry . --ignore-missing foo,bar`.
    """,
    default=(),
)
@click.option(
    "--ignore-transitive",
    "-it",
    type=COMMA_SEPARATED_TUPLE,
    help="""Comma-separated list of dependencies that should never be marked as an issue due to it being a transitive dependency, even though deptry determines them to be transitive.
    For example; `deptry . --ignore-transitive foo,bar`.
    """,
    default=(),
)
@click.option(
    "--ignore-misplaced-dev",
    "-id",
    type=COMMA_SEPARATED_TUPLE,
    help="""Comma-separated list of modules that should never be marked as a misplaced development dependency, even though it seems to not be used solely for development purposes.
    For example; `deptry . --ignore-misplaced-dev foo,bar`.
    """,
    default=(),
)
@click.option(
    "--exclude",
    "-e",
    multiple=True,
    type=str,
    help="""A regular expression for directories or files in which .py files should not be scanned for imports to determine if there are dependency issues.
    Can be used multiple times by specifying the argument multiple times. re.match() is used to match the expressions, which by default checks for a match only at the beginning of a string.
    For example: `deptry . -e ".*/foo/" -e bar"` Note that this overwrites the defaults.
    """,
    default=("venv", r"\.venv", r"\.direnv", "tests", r"\.git", "setup.py"),
    show_default=True,
)
@click.option(
    "--extend-exclude",
    "-ee",
    type=str,
    multiple=True,
    help="""Like --exclude, but adds additional files and directories on top of the excluded ones instead of overwriting the defaults.
    (Useful if you simply want to add to the default) `deptry . -ee ".*/foo/" -ee bar"`""",
    default=(),
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
    is_eager=True,
    expose_value=False,
    callback=display_deptry_version,
    help="Display the current version and exit.",
)
@click.option(
    "--requirements-txt",
    "-rt",
    type=COMMA_SEPARATED_TUPLE,
    help=""".txt files to scan for dependencies. If a file called pyproject.toml with a [tool.poetry.dependencies] section is found, this argument is ignored
    and the dependencies are extracted from the pyproject.toml file instead. Can be multiple e.g. `deptry . --requirements-txt req/prod.txt,req/extra.txt`""",
    default=("requirements.txt",),
    show_default=True,
)
@click.option(
    "--requirements-txt-dev",
    "-rtd",
    type=COMMA_SEPARATED_TUPLE,
    help=""".txt files to scan for additional development dependencies. If a file called pyproject.toml with a [tool.poetry.dependencies] section is found, this argument is ignored
    and the dependencies are extracted from the pyproject.toml file instead. Can be multiple e.g. `deptry . --requirements-txt-dev req/dev.txt,req/test.txt`""",
    default=("dev-requirements.txt", "requirements-dev.txt"),
    show_default=True,
)
@click.option(
    "--json-output",
    "-o",
    type=str,
    help="""If specified, a summary of the dependency issues found will be written to the output location specified. e.g. `deptry . -o deptry.json`""",
    show_default=True,
)
def deptry(
    root: Path,
    config: Path,
    ignore_obsolete: tuple[str, ...],
    ignore_missing: tuple[str, ...],
    ignore_transitive: tuple[str, ...],
    ignore_misplaced_dev: tuple[str, ...],
    skip_obsolete: bool,
    skip_missing: bool,
    skip_transitive: bool,
    skip_misplaced_dev: bool,
    exclude: tuple[str, ...],
    extend_exclude: tuple[str, ...],
    ignore_notebooks: bool,
    requirements_txt: tuple[str, ...],
    requirements_txt_dev: tuple[str, ...],
    json_output: str,
) -> None:
    """Find dependency issues in your Python project.

    [ROOT] is the path to the root directory of the project to be scanned.
    All other arguments should be specified relative to [ROOT].

    """

    Core(
        root=root,
        config=config,
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
