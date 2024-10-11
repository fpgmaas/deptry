from __future__ import annotations

import re
from collections import defaultdict
from functools import lru_cache

from deptry.compat import importlib_metadata


@lru_cache(maxsize=None)
def normalize_distribution_name(name: str) -> str:
    """
    Apply name normalization on distribution name, per https://packaging.python.org/en/latest/specifications/name-normalization/#name-normalization.
    """
    return re.sub(r"[-_.]+", "-", name).lower()


@lru_cache(maxsize=1)
def get_packages_normalized_distributions() -> dict[str, set[str]]:
    """
    Return a mapping of top-level packages to their normalized distributions.
    Cache ensures that we only build this mapping once, since it should not change during the invocation of deptry.
    """
    return {
        package: {normalize_distribution_name(distribution) for distribution in distributions}
        for package, distributions in importlib_metadata.packages_distributions().items()
    }


@lru_cache(maxsize=1)
def get_normalized_distributions_packages() -> dict[str, set[str]]:
    """
    Return a mapping of normalized distributions to their top-level packages.
    Cache ensures that we only build this mapping once, since it should not change during the invocation of deptry.
    """
    distributions_packages: dict[str, set[str]] = defaultdict(set)

    for package, distributions in get_packages_normalized_distributions().items():
        for distribution in distributions:
            distributions_packages[distribution].add(package)

    return dict(distributions_packages)


def get_distributions_from_package(name: str) -> set[str] | None:
    """
    Retrieve the distributions provided by the package, if any.
    """
    return get_packages_normalized_distributions().get(name)


def get_packages_from_distribution(name: str) -> set[str] | None:
    """
    Normalize the distribution and retrieve the packages it provides, if any.
    """
    return get_normalized_distributions_packages().get(normalize_distribution_name(name))
