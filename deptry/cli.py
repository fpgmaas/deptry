from __future__ import annotations

import logging
import sys
from collections import defaultdict
from importlib.metadata import version
from pathlib import Path
from typing import TYPE_CHECKING

import click

from deptry.config import read_configuration_from_pyproject_toml
from deptry.core import Core

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

if sys.platform == "win32":
    from colorama import just_fix_windows_console

    just_fix_windows_console()

DEFAULT_EXCLUDE = ("venv", r"\.venv", r"\.direnv", "tests", r"\.git", r"setup\.py")


class CommaSeparatedTupleParamType(click.ParamType):
    """
    This class is used to uniformly handle configuration parameters that can be either passed as a comma-separated string,
    as a list of strings, or as a tuple of strings. For example, the value for a parameter can be a comma-separated string
    when passed as a command line argument, or as a list of strings when passed through pyproject.toml.
    """

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


class CommaSeparatedMappingParamType(click.ParamType):
    """
    This class is used to uniformly handle configuration parameters that can be either passed as a comma-separated pair
    string, or as a Mapping of strings to tuples of strings. Items in a pair string are separated by an equal sign,
    where multiple values are separated by a pipe: key1=value1,key2=value2|value3.
    For example, the value for a parameter can be a comma-separated pair string when passed as a command line argument,
    or as a mapping of string to tuples of strings when passed through pyproject.toml.
    """

    name = "mapping"

    def convert(
        self,
        # In the mapping value below, although a str is a Sequence[str] itself,
        # they are treated differently from other sequences of str.
        value: str | Mapping[str, Sequence[str] | str],
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> dict[str, tuple[str, ...]]:
        converted: dict[str, tuple[str, ...]]
        if isinstance(value, str):
            map_: defaultdict[str, list[str]] = defaultdict(list)
            for item in value.split(","):
                pair = tuple(item.split("=", 1))
                if len(pair) != 2:
                    error_msg = (
                        f"package name and module names pairs should be concatenated with an equal sign (=): {item}"
                    )
                    raise ValueError(error_msg)
                package_name = pair[0]
                module_names = pair[1].split("|")
                map_[package_name].extend(module_names)
            converted = {k: tuple(v) for k, v in map_.items()}
        else:
            converted = {k: (v,) if isinstance(v, str) else tuple(v) for k, v in value.items()}

        return converted


COMMA_SEPARATED_MAPPING = CommaSeparatedMappingParamType()


def configure_logger(_ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    log_level = logging.DEBUG if value else logging.INFO
    logging.basicConfig(level=log_level, handlers=[logging.StreamHandler()], format="%(message)s")


def display_deptry_version(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    if not value or ctx.resilient_parsing:
        return None

    click.echo(f'deptry {version("deptry")}')
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
    "--no-ansi",
    is_flag=True,
    help="Disable ANSI characters in terminal output.",
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
    help=f"""A regular expression for directories or files in which .py files should not be scanned for imports to determine if there are dependency issues.
    Can be used multiple times by specifying the argument multiple times. re.match() is used to match the expressions, which by default checks for a match only at the beginning of a string.
    For example: `deptry . -e ".*/foo/" -e bar"` Note that this overwrites the defaults.
    [default: {", ".join(DEFAULT_EXCLUDE)}
    """,
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
    "--known-first-party",
    "-kf",
    type=str,
    multiple=True,
    help="Modules to consider as first party ones.",
    default=(),
    show_default=True,
)
@click.option(
    "--json-output",
    "-o",
    type=str,
    help="""If specified, a summary of the dependency issues found will be written to the output location specified. e.g. `deptry . -o deptry.json`""",
    show_default=True,
)
@click.option(
    "--package-module-name-map",
    "-pmnm",
    type=COMMA_SEPARATED_MAPPING,
    help="""Manually defined module names belonging to packages. For example; `deptry . --package-module-name-map package_1=module_a,package_2=module_b|module_c`.""",
    default={},
    show_default=False,
)
def deptry(
    root: Path,
    config: Path,
    no_ansi: bool,
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
    known_first_party: tuple[str, ...],
    json_output: str,
    package_module_name_map: Mapping[str, Sequence[str]],
) -> None:
    """Find dependency issues in your Python project.

    [ROOT] is the path to the root directory of the project to be scanned.
    All other arguments should be specified relative to [ROOT].

    """

    Core(
        root=root,
        config=config,
        no_ansi=no_ansi,
        ignore_obsolete=ignore_obsolete,
        ignore_missing=ignore_missing,
        ignore_transitive=ignore_transitive,
        ignore_misplaced_dev=ignore_misplaced_dev,
        exclude=exclude or DEFAULT_EXCLUDE,
        extend_exclude=extend_exclude,
        using_default_exclude=not exclude,
        ignore_notebooks=ignore_notebooks,
        skip_obsolete=skip_obsolete,
        skip_missing=skip_missing,
        skip_transitive=skip_transitive,
        skip_misplaced_dev=skip_misplaced_dev,
        requirements_txt=requirements_txt,
        requirements_txt_dev=requirements_txt_dev,
        known_first_party=known_first_party,
        json_output=json_output,
        package_module_name_map=package_module_name_map,
    ).run()
