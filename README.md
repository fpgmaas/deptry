# deptry

[![Release](https://img.shields.io/github/v/release/fpgmaas/deptry)](https://img.shields.io/github/v/release/fpgmaas/deptry)
[![Build status](https://img.shields.io/github/workflow/status/fpgmaas/deptry/merge-to-main)](https://img.shields.io/github/workflow/status/fpgmaas/deptry/merge-to-main)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/deptry)](https://pypi.org/project/deptry/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/deptry)](https://img.shields.io/pypi/dm/deptry?style=flat-square)
[![License](https://img.shields.io/github/license/fpgmaas/deptry)](https://img.shields.io/github/license/fpgmaas/deptry)

---

_deptry_ is a command line tool to check for issues with dependencies in a poetry managed Python project. It checks for four types of issues:

- Obsolete dependencies: Dependencies which are added to your project's dependencies, but which are not used within the codebase.
- Missing dependencies: Modules that are imported within your project, but no corresponding package is found in the environment.
- Transitive dependencies: Packages from which code is imported, but the package (A) itself is not in your projects dependencies. Instead, another package (B) is in your list of dependencies, which depends on (A). Package (A) should be added to your project's list of dependencies.
- Misplaced dependencies: Development dependencies that should be included as regular dependencies.

_deptry_ detects these issue by scanning the imported modules within all Python files in 
a directory and it's subdirectories, and comparing those to the dependencies listed in _pyproject.toml_.

---

**Documentation**: <https://fpgmaas.github.io/deptry/>

---

## Quickstart

### Installation

_deptry_ can be added to your project with 

```
poetry add --group dev deptry
```

or for older versions of poetry:

```
poetry add --dev deptry
```

### Prerequisites

In order to check for obsolete imports, _deptry_ requires a _pyproject.toml_ file to be present in the directory passed as the first argument, and it requires the corresponding environment to be activated.

### Usage

To scan your project for obsolete imports, run

```sh
deptry .
```

__deptry__ can be configured by using additional command line arguments, or 
by adding a `[tool.deptry]` section in __pyproject.toml__.

For more information, see the [documentation](https://fpgmaas.github.io/deptry/).

---

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).