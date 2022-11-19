import sys
from itertools import chain
from pathlib import Path
from typing import Optional

from deptry.compat import metadata


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


def in_project_virtualenv(
    project_name: str, *, prefix: str, base_prefix: str, active_virtual_env: Optional[str] = None
) -> bool:
    """Determine if a project virtualenv is active"""

    # Gobal installation
    if prefix == base_prefix:
        return False

    # No virtualenv has been activated. Unless the project name is in
    # the interpreter path, assume we are not in the project's virtualenv
    if not active_virtual_env:
        return project_name in prefix

    # A virtualenv has been activated. But if `deptry` was installed gloabally using
    # `pipx`, we could be running in another installation.
    return active_virtual_env == prefix


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
