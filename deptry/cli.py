import argparse
import logging
import sys

import click

from deptry.core import Core


@click.group()
def deptry():
    pass


@click.command()
@click.option("--verbose", "-v", is_flag=True, help="Print more output.")
@click.option("--ignore-packages", "-ip", multiple=True)
def check(verbose, ignore_packages):
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level, handlers=[logging.StreamHandler()], format="%(message)s")

    obsolete_dependencies = Core(ignore_packages=list(ignore_packages)).run()
    if len(obsolete_dependencies):
        logging.info(f"pyproject.toml contains obsolete dependencies: {obsolete_dependencies}")
        exit(1)
    else:
        exit(0)


deptry.add_command(check)
