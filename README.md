# deptry

[![Release](https://img.shields.io/github/v/release/fpgmaas/deptry)](https://img.shields.io/github/v/release/fpgmaas/deptry)
[![Build status](https://img.shields.io/github/workflow/status/fpgmaas/deptry/merge-to-main)](https://img.shields.io/github/workflow/status/fpgmaas/deptry/merge-to-main)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/deptry)](https://pypi.org/project/deptry/)
[![codecov](https://codecov.io/gh/fpgmaas/deptry/branch/main/graph/badge.svg)](https://codecov.io/gh/fpgmaas/deptry)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/deptry)](https://img.shields.io/pypi/dm/deptry?style=flat-square)
[![License](https://img.shields.io/github/license/fpgmaas/deptry)](https://img.shields.io/github/license/fpgmaas/deptry)

---

_deptry_ is a command line tool to check for issues with dependencies in a poetry managed Python project, such as obsolete or missing dependencies.

Dependency issues are detected by scanning for imported modules within all Python files in a directory and its subdirectories, and comparing those to the dependencies listed in pyproject.toml.

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

> **Warning**
> _deptry_ is still in the early phases of development. For one-off testing of your project's dependencies, this is no issue. However, if you plan to use _deptry_ in a CI/CD pipeline, it is a good idea to pin the version.

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