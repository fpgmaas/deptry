import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path

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


def install_metadata_finder(site_packages: Path) -> None:
    """Add poject virtualenv site packages to metadata search path"""
    path = [str(site_packages.absolute()), *sys.path]

    class VirtualenvDistributionFinder(metadata.MetadataPathFinder):
        @classmethod
        def find_distributions(cls, context):
            context = metadata.DistributionFinder.Context(name=context.name, path=path)
            return super().find_distributions(context)

    sys.meta_path.insert(0, VirtualenvDistributionFinder())


def warn_if_not_running_in_virtualenv(root: Path) -> None:
    ctx = ExecutionContext.from_runtime(root)
    if ctx.running_in_project_virtualenv():
        logging.warn("foo")
        return
    log_msg = (
        f"If deptry is not running within the `{ctx.project_name}` project's virtual environment"
        " consider using the `--python-site-packages` option to locate package metadata"
    )
    logging.warning(log_msg)
