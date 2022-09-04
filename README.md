# deptry

[![Release](https://img.shields.io/github/v/release/fpgmaas/deptry)](https://img.shields.io/github/v/release/fpgmaas/deptry)
[![Build status](https://img.shields.io/github/workflow/status/fpgmaas/deptry/merge-to-main)](https://img.shields.io/github/workflow/status/fpgmaas/deptry/merge-to-main)
[![Commit activity](https://img.shields.io/github/commit-activity/m/fpgmaas/deptry)](https://img.shields.io/github/commit-activity/m/fpgmaas/deptry)
[![Docs](https://img.shields.io/badge/docs-gh--pages-blue)](https://fpgmaas.github.io/deptry/)
[![Code style with black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports with isort](https://img.shields.io/badge/%20imports-isort-%231674b1)](https://pycqa.github.io/isort/)
[![License](https://img.shields.io/github/license/fpgmaas/deptry)](https://img.shields.io/github/license/fpgmaas/deptry)

---

_deptry_ is a command line tool to check for unused dependencies in a poetry managed Python project. It does so by scanning the imported modules within all Python files in 
a directory and it's subdirectories, and comparing those to the dependencies listed in `pyproject.toml`. 

---

**Documentation**: <https://fpgmaas.github.io/deptry/>

---

## Installation and usage

### Installation

__deptry__ can be added to your project with 

```
poetry add deptry
```

Alternatively, it can be installed with `pip install deptry`.

### Prerequisites

In order to check for obsolete imports, __deptry__ should be run directly within the directory that contains the __pyproject.toml__ file, and it requires the environment created with __pyproject.toml__ to be activated.

### Usage

To scan your project for obsolete imports, run

```sh
deptry .
```

or for a more verbose version

```sh
deptry . -v
```

__deptry__ can be configured by using additional command line arguments, or 
by adding a `[tool.deptry]` section in __pyproject.toml__.

For more information, see the [documentation](https://fpgmaas.github.io/deptry/).

---

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).