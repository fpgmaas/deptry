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
    "--ignore-obsolete",
    "-io",
    multiple=True,
    help="""
    Dependencies listed in pyproject.toml that should never be marked as obsolete, even if they are not imported in any of the files scanned.
    Can be used multiple times. For example; `deptry . -io dependency-1 -io dependency-2`.
    """,
)
@click.option(
    "--ignore-missing",
    "-im",
    multiple=True,
    help="""Modules that should never be marked as having missing dependencies, even if the matching package for the import statement cannot be found.
    Can be used multiple times. For example; `deptry . -io module_1 -io module_2`.""",
)
@click.option(
    "--ignore-transitive",
    "-it",
    multiple=True,
    help="""Modules that should never be marked as 'missing due to transitive' even though deptry determines them to be transitive. 
    Can be used multiple times. For example; `deptry . -it module_1 -io module_2`.""",
)
@click.option(
    "--ignore-directories",
    "-id",
    multiple=True,
    help="""Directories in which .py files should not be scanned for imports to determine if dependencies are obsolete, missing or transitive.
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
    ignore_obsolete: List[str],
    ignore_missing: List[str],
    ignore_transitive: List[str],
    skip_obsolete: bool = False,
    skip_missing: bool = False,
    skip_transitive: bool = False,
    ignore_directories: List[str],
    ignore_notebooks: bool
) -> None:

    with run_within_dir(directory):
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(level=log_level, handlers=[logging.StreamHandler()], format="%(message)s")

        # Pass the CLI arguments to Config, if they are provided, otherwise pass 'None'.
        # This way, we can distinguish if a argument was actually passed by the user
        # (e.g. ignore_notebooks is 'False' by default).
        config = Config(
            ignore_obsolete=ignore_obsolete if ignore_obsolete else None,
            ignore_missing=ignore_missing if ignore_missing else None,
            ignore_transitive=ignore_transitive if ignore_transitive else None,
            ignore_directories=ignore_directories if ignore_directories else None,
            ignore_notebooks=ignore_notebooks if ignore_notebooks else None,
            skip_obsolete=skip_obsolete if skip_obsolete else None,
            skip_missing=skip_missing if skip_missing else None,
            skip_transitive=skip_transitive if skip_transitive else None,
        )

        dependencies = Core(
            ignore_obsolete=ignore_obsolete,
            ignore_missing=ignore_missing,
            ignore_transitive=ignore_transitive,
            ignore_directories=config.ignore_directories,
            ignore_notebooks=config.ignore_notebooks,
            skip_obsolete = skip_obsolete,
            skip_missing = skip_missing,
            skip_transitive = skip_transitive
        ).run()
        sep = "\n\t"
        issue_found = False
        if not skip_obsolete and len(dependencies['obsolete']):
            log_obsolete_dependencies(dependencies['obsolete'])
            issue_found = True
        if not skip_missing and len(dependencies['missing']):
            log_missing_dependencies(dependencies['missing'])
            issue_found = True
        if not skip_transitive and len(dependencies['transitive']):
            log_transitive_dependencies(dependencies['transitive'])
            issue_found = True

        if issue_found:
            log_additional_info()
            sys.exit(1)
        else:
            # TODO: adapt message below; e.g. if only checking for obsolete and transitive, display 'No obsolete or transitive dependencies found' etc
            logging.info("Success! No obsolete, missing, or transitive dependencies found.")
            sys.exit(0)

def log_obsolete_dependencies(dependencies: List[str], sep = "\n\t") -> None:
    logging.info(f"pyproject.toml contains obsolete dependencies:\n{sep}{sep.join(dependencies)}\n")
    logging.info(
        """Consider removing them from your projects dependencies. If a package is used for development purposes, you should add 
it to your development dependencies instead.
"""
    )

def log_missing_dependencies(dependencies: List[str], sep = "\n\t") -> None:
    logging.info(f"There are dependencies missing from pyproject.toml:\n{sep}{sep.join(dependencies)}\n")
    logging.info(
        """Consider adding them to your project's dependencies. 
"""
    )

def log_transitive_dependencies(dependencies: List[str], sep = "\n\t") -> None:
    logging.info(f"There are transitive dependencies that should be explicitly defined in pyproject.toml:\n{sep}{sep.join(dependencies)}\n")
    logging.info(
        """They are currently imported but not specified directly as your project's dependencies, or the package is not available in the
currently active environment. If this is because it is a conditional dependency, please add it to the `ignore_dependencies` flag.
"""
    )

def log_additional_info():
    logging.info("""Dependencies and directories can be ignored by passing additional command-line arguments. See `deptry --help` for more details.
Alternatively, deptry can be configured through `pyproject.toml`:

```
ignore_dependencies = [
  'your_dependency'
]
ignore_directories = [
  '.venv', 'tests'
]
```

For more information, see the documentation: https://fpgmaas.github.io/deptry/
If you have encountered a bug, have a feature request or if you have any other feedback, please file a bug report at https://github.com/fpgmaas/deptry/issues/new/choose.

""")