<p align="center">
  <img width="460" height="300" src="https://raw.githubusercontent.com/fpgmaas/deptry/main/docs/docs/static/deptry_Logo-01.svg">
</p>

---

[![Release](https://img.shields.io/github/v/release/fpgmaas/deptry)](https://img.shields.io/github/v/release/fpgmaas/deptry)
[![Build status](https://img.shields.io/github/workflow/status/fpgmaas/deptry/merge-to-main)](https://img.shields.io/github/workflow/status/fpgmaas/deptry/merge-to-main)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/deptry)](https://pypi.org/project/deptry/)
[![codecov](https://codecov.io/gh/fpgmaas/deptry/branch/main/graph/badge.svg)](https://codecov.io/gh/fpgmaas/deptry)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/deptry)](https://img.shields.io/pypi/dm/deptry?style=flat-square)
[![License](https://img.shields.io/github/license/fpgmaas/deptry)](https://img.shields.io/github/license/fpgmaas/deptry)

_deptry_ is a command line tool to check for issues with dependencies in a Python project, such as obsolete or missing dependencies. It supports the following types of projects:

- Projects that use [Poetry](https://python-poetry.org/) and a corresponding _pyproject.toml_ file
- Projects that use [PDM](https://pdm.fming.dev/latest/) and a corresponding _pyproject.toml_ file
- Projects that use a _requirements.txt_ file according to the [pip](https://pip.pypa.io/en/stable/user_guide/) standards

Dependency issues are detected by scanning for imported modules within all Python files in a directory and its subdirectories, and comparing those to the dependencies listed in the project's requirements.

---
<p align="center">
  <a href = "https://fpgmaas.github.io/deptry">Link to the documentation</a>
</p>

---

## Quickstart

### Installation

_deptry_ can be added to your project with 

```shell
poetry add --group dev deptry
```

or with 

```
<activate virtual environment>
pip install deptry
```

> **Warning**
> When using pip to install _deptry_, make sure you install it within the virtual environment of your project. Installing _deptry_ globally will not work, since it needs to have access to the metadata of the packages in the virtual environment.

### Prerequisites

_deptry_ should be run withing the root directory of the project to be scanned, and the project should be running in its own dedicated virtual environment.

### Usage

To scan your project for dependency issues, run

```sh
deptry .
```

_deptry_ can be configured by using additional command line arguments, or 
by adding a `[tool.deptry]` section in _pyproject.toml_.

For more information, see the [documentation](https://fpgmaas.github.io/deptry/).

---

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).
