import logging
import os
import sys
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import Optional

from deptry.compat import metadata


@dataclass
class ExecutionContext:
    project_root: Path
    base_prefix: str
    prefix: str
    active_virtual_env: str = None

    @classmethod
    def from_runtime(cls, project_root: Path):
        return cls(
            project_root=project_root,
            base_prefix=sys.base_prefix,
            prefix=sys.prefix,
            active_virtual_env=os.environ.get("VIRTUAL_ENV"),
        )

    @property
    def project_name(self):
        return self.project_root.absolute().name

    def running_in_project_virtualenv(self) -> bool:
        """Determine if executed by the interpreter in the project's virtual environment

        If we are executed from virtual environment, the context `prefix`
        will be set to the virtual environment's directory, whereas
        `base_prefix` will point to the global Python installation
        used to create the virtual environment.

        The `active_virtual_env` context field holds the value of the
        VIRTUAL_ENV environment variable, that tells with good reliability
        that a virtual environment has been activated in the current shell.
        """

        # Gobal installation
        if self.prefix == self.base_prefix:
            return False

        # No virtualenv has been activated. Unless the project name is in
        # the interpreter path, assume we are not in the project's virtualenv
        if not self.active_virtual_env:
            return self.project_name in self.prefix

        # A virtualenv has been activated. But if `deptry` was installed gloabally using
        # `pipx`, we could be running in another installation.
        return self.active_virtual_env == self.prefix


def find_site_packages_in(root: Path) -> Optional[Path]:
    """Find site packages directory under a virtual environment root

    Two layouts are tried: `lib/pythonX.X/site-packages` and
    `Lib/site-packages`, the latter specific to Windows.
    """
    search = chain(root.rglob("lib/python*/site-packages"), root.rglob("Lib/site-packages"))
    try:
        return next(search)
    except StopIteration:
        return None


def guess_virtualenv_site_packages(project_root: Path, active_virtual_env: Optional[str] = None) -> Optional[Path]:
    """Try to locate a project's virtualenv packages using environment and popular locations"""
    site_packages = None
    possible_roots = [
        Path("~/.virtualenvs").expanduser() / project_root.name,
        project_root / ".venv",
    ]
    if active_virtual_env:
        possible_roots.append(Path(active_virtual_env))

    while not site_packages and possible_roots:
        site_packages = find_site_packages_in(possible_roots.pop())

    return site_packages


def install_distribution_finder(site_packages: Path) -> None:
    path = [str(site_packages.absolute()), *sys.path]

    class VirtualenvDistributionFinder(metadata.MetadataPathFinder):
        @classmethod
        def find_distributions(cls, context):
            context = metadata.DistributionFinder.Context(name=context.name, path=path)
            return super().find_distributions(context)

    sys.meta_path.insert(0, VirtualenvDistributionFinder())


def install_metadata_finder(ctx: ExecutionContext) -> None:
    """Add poject virtualenv site packages to metadata search path"""

    # Try to locate the project's virtual environment site packages
    # and add it to the dependency metadata search path.
    site_packages = guess_virtualenv_site_packages(ctx.project_root, ctx.active_virtual_env)
    if site_packages:
        logging.warning(f"Assuming virtual environment for project {ctx.project_name} is {site_packages}")
        logging.warning("Consider installing deptry in this environment.")
    install_distribution_finder(site_packages)
