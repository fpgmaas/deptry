# poetry-check-deps

[![Release](https://img.shields.io/github/v/release/fpgmaas/poetry-check-deps)](https://img.shields.io/github/v/release/fpgmaas/poetry-check-deps)
[![Build status](https://img.shields.io/github/workflow/status/fpgmaas/poetry-check-deps/merge-to-main)](https://img.shields.io/github/workflow/status/fpgmaas/poetry-check-deps/merge-to-main)
[![Commit activity](https://img.shields.io/github/commit-activity/m/fpgmaas/poetry-check-deps)](https://img.shields.io/github/commit-activity/m/fpgmaas/poetry-check-deps)
[![Docs](https://img.shields.io/badge/docs-gh--pages-blue)](https://fpgmaas.github.io/poetry-check-deps/)
[![Code style with black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports with isort](https://img.shields.io/badge/%20imports-isort-%231674b1)](https://pycqa.github.io/isort/)
[![License](https://img.shields.io/github/license/fpgmaas/poetry-check-deps)](https://img.shields.io/github/license/fpgmaas/poetry-check-deps)

A repository to check for unused dependencies in a poetry managed python project

- **Github repository**: <https://github.com/fpgmaas/poetry-check-deps/>
- **Documentation** <https://fpgmaas.github.io/poetry-check-deps/>

## Releasing a new version

- Create an API Token on [Pypi](https://pypi.org/).
- Add the API Token to your projects secrets with the name `PYPI_TOKEN` by visiting 
[this page](https://github.com/fpgmaas/poetry-check-deps/settings/secrets/actions/new).
- Create a [new release](https://github.com/fpgmaas/poetry-check-deps/releases/new) on Github. 
Create a new tag in the form ``*.*.*``.

For more details, see [here](https://fpgmaas.github.io/cookiecutter-poetry/releasing.html).

---

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).