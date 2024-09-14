from __future__ import annotations

from unittest.mock import patch

import pytest

from deptry.distribution import (
    get_distributions_from_package,
    get_normalized_distributions_packages,
    get_packages_from_distribution,
    get_packages_normalized_distributions,
    normalize_distribution_name,
)


@pytest.mark.parametrize(
    "name",
    [
        "friendly-bard",
        "Friendly-Bard",
        "FRIENDLY-BARD",
        "friendly.bard",
        "friendly_bard",
        "friendly--bard",
        "FrIeNdLy-._.-bArD",
    ],
)
def test_normalize_distribution_name(name: str) -> None:
    assert normalize_distribution_name(name) == "friendly-bard"


def test_get_packages_normalized_distributions() -> None:
    # Clear cache before calling the function, as it is also populated during testing.
    get_packages_normalized_distributions.cache_clear()

    with patch(
        "deptry.distribution.importlib_metadata.packages_distributions",
        return_value={
            "requests": ["requests"],
            "charset_normalizer": ["Charset_Normalizer"],
            "bs4": ["beautifulsoup4"],
            "_distutils_hack": ["setuptools"],
            "pkg_resources": ["setuptools"],
            "setuptools": ["setuptools"],
        },
    ) as mock_packages_distributions:
        normalized_packages_distributions = get_packages_normalized_distributions()

        # Call function a second time, to ensure that we only call `packages_distributions` once.
        get_packages_normalized_distributions()

    # Clear cache after calling the function to avoid keeping our mocked values, in case test invocation depend on it.
    get_packages_normalized_distributions.cache_clear()

    assert normalized_packages_distributions == {
        "requests": {"requests"},
        "charset_normalizer": {"charset-normalizer"},
        "bs4": {"beautifulsoup4"},
        "_distutils_hack": {"setuptools"},
        "pkg_resources": {"setuptools"},
        "setuptools": {"setuptools"},
    }
    mock_packages_distributions.assert_called_once()


def test_get_normalized_distributions_packages() -> None:
    # Clear cache before calling the function, as it is also populated during testing.
    get_normalized_distributions_packages.cache_clear()

    with patch(
        "deptry.distribution.get_packages_normalized_distributions",
        return_value={
            "requests": {"requests"},
            "charset_normalizer": {"charset-normalizer"},
            "bs4": {"beautifulsoup4"},
            "_distutils_hack": {"setuptools"},
            "pkg_resources": {"setuptools"},
            "setuptools": {"setuptools"},
        },
    ) as mock_packages_distributions:
        distributions_packages = get_normalized_distributions_packages()

        # Call function a second time, to ensure that we only call `packages_distributions` once.
        get_normalized_distributions_packages()

    # Clear cache after calling the function to avoid keeping our mocked values, in case test invocation depend on it.
    get_normalized_distributions_packages.cache_clear()

    assert distributions_packages == {
        "requests": {"requests"},
        "charset-normalizer": {"charset_normalizer"},
        "beautifulsoup4": {"bs4"},
        "setuptools": {"_distutils_hack", "pkg_resources", "setuptools"},
    }
    mock_packages_distributions.assert_called_once()


def test_get_distributions_from_package() -> None:
    with patch(
        "deptry.distribution.get_packages_normalized_distributions",
        return_value={
            "bar": {"foo-bar"},
            "foo": {"foo-bar", "foo"},
        },
    ):
        assert get_distributions_from_package("foo") == {"foo-bar", "foo"}


def test_get_packages_from_distribution() -> None:
    with patch("deptry.distribution.get_normalized_distributions_packages", return_value={"foo-bar": {"bar", "foo"}}):
        assert get_packages_from_distribution("foo_Bar") == {"bar", "foo"}
