import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, Optional

from deptry.compat import metadata

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

PYPROJECT_TOML_PATH = "./pyproject.toml"


@contextmanager
def run_within_dir(path: Path) -> Generator[None, None, None]:
    """
    Utility function to run some code within a directory, and change back to the current directory afterwards.

    Example usage:

    ```
    with run_within_dir(directory):
        some_code()
    ```

    """
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def load_pyproject_toml(pyproject_toml_path: str = PYPROJECT_TOML_PATH) -> Dict[str, Any]:
    try:
        with Path(pyproject_toml_path).open("rb") as pyproject_file:
            return tomllib.load(pyproject_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"No file `pyproject.toml` found in directory {os.getcwd()}")


def find_site_packages_below(root: Path, platform: str) -> Optional[Path]:
    """Find site packages directory below a virtual environment root"""
    if platform == "Windows":
        pattern = "Lib/site-packages"
    else:
        pattern = "lib/python*/site-packages"
    try:
        return next(root.rglob(pattern))
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


def guess_virtualenv_site_packages(
    project_root: Path, platform: str, active_virtual_env: Optional[str] = None
) -> Optional[Path]:
    """Try to locate a project's virtualenv packages using environment and popular locations"""
    site_packages = None
    possible_roots = [
        Path("~/.virtualenvs").expanduser() / project_root.name,
        project_root / ".venv",
    ]
    if active_virtual_env:
        possible_roots.append(Path(active_virtual_env))

    while not site_packages and possible_roots:
        site_packages = find_site_packages_below(possible_roots.pop(), platform=platform)

    return site_packages


def install_distribution_finder(site_packages: Path) -> None:
    path = [str(site_packages.absolute()), *sys.path]

    class VirtualenvDistributionFinder(metadata.MetadataPathFinder):
        @classmethod
        def find_distributions(cls, context):
            context = metadata.DistributionFinder.Context(name=context.name, path=path)
            return super().find_distributions(context)

    sys.meta_path.insert(0, VirtualenvDistributionFinder())
