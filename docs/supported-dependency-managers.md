# Supported dependency managers

While most dependency managers support the
standard [PEP 621 format](https://packaging.python.org/en/latest/specifications/pyproject-toml/) for defining
dependencies in `pyproject.toml`, not all of them do. Even those that do often provide additional ways to define
dependencies that are not standardized.

_deptry_ can extract dependencies from most of the package managers that support PEP
621 (e.g. [uv](https://docs.astral.sh/uv/), [PDM](https://pdm-project.org/en/latest/)), including tool-specific
extensions, but also from package managers that do not (or used to not) support PEP
621 (e.g. [Poetry](https://python-poetry.org/), [pip](https://pip.pypa.io/en/stable/reference/requirements-file-format/)).

## PEP 621

_deptry_ fully supports [PEP 621 standard](https://packaging.python.org/en/latest/specifications/pyproject-toml/), and
uses the presence of a `[project]` section in `pyproject.toml` to determine that the project uses PEP 621.

By default, _deptry_ extracts, from `pyproject.toml`:

- regular dependencies from:
    - `dependencies` entry under `[project]` section
    - groups under `[project.optional-dependencies]` section
- development dependencies from groups under `[dependency-groups]` section

For instance, with this `pyproject.toml`:

```toml title="pyproject.toml"
[project]
name = "foo"
dependencies = ["orjson>=3.0.0"]

[project.optional-dependencies]
cli = ["click>=8.0.0"]
http = [
    "httpx>=0.27.0",
    "uvicorn>=0.32.0",
]

[dependency-groups]
docs = ["mkdocs==1.6.1"]
test = [
    "pytest==8.3.3",
    "pytest-cov==5.0.0",
]
```

the following dependencies will be extracted:

- regular dependencies: `orjson`, `click`, `httpx`, `uvicorn`
- development dependencies: `mkdocs`, `pytest`, `pytest-cov`

!!! note

    Groups under `[project.optional-dependencies]` can be flagged as development dependency groups by
    using [`--pep621-dev-dependency-groups`](usage.md#pep-621-dev-dependency-groups) argument (or its
    `pep_621_dev_dependency_groups` equivalent in `pyproject.toml`).

### uv

Additionally to PEP 621 dependencies, _deptry_ will
extract [uv development dependencies](https://docs.astral.sh/uv/concepts/dependencies/#development-dependencies) from
`dev-dependencies` entry under `[tool.uv]` section, for instance:

```toml title="pyproject.toml"
[tool.uv]
dev-dependencies = [
    "mkdocs==1.6.1",
    "pytest==8.3.3",
    "pytest-cov==5.0.0",
]
```

### PDM

Additionally to PEP 621 dependencies, _deptry_ will
extract [PDM development dependencies](https://pdm-project.org/en/latest/usage/dependency/#add-development-only-dependencies)
from `[tool.pdm.dev-dependencies]` section, for instance:

```toml title="pyproject.toml"
[tool.pdm.dev-dependencies]
docs = ["mkdocs==1.6.1"]
test = [
    "pytest==8.3.3",
    "pytest-cov==5.0.0",
]
```

### Setuptools

When using setuptools as a build backend, both `dependencies` and `optional-dependencies` can
be [dynamically read](https://setuptools.pypa.io/en/stable/userguide/pyproject_config.html#dynamic-metadata) from
`requirements.txt`-format files, for instance:

```toml title="pyproject.toml"
[build-backend]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "foo"
dynamic = ["dependencies", "optional-dependencies"]

[tool.setuptools.dynamic]
dependencies = { file = ["requirements.txt"] }

[tool.setuptools.dynamic.optional-dependencies]
cli = { file = ["cli-requirements.txt"] }
```

In this example, regular dependencies will be extracted from both `requirements.txt` and `cli-requirements.txt` files.

!!! note

    Groups under `[tool.setuptools.dynamic.optional-dependencies]` can be flagged as development dependency groups by
    using [`--pep621-dev-dependency-groups`](usage.md#pep-621-dev-dependency-groups) argument (or its
    `pep_621_dev_dependency_groups` equivalent in `pyproject.toml`).

## Poetry

_deptry_ supports
extracting [dependencies defined using Poetry](https://python-poetry.org/docs/pyproject/#dependencies-and-dependency-groups),
and uses the presence of a `[tool.poetry.dependencies]` section in `pyproject.toml` to determine that the project uses
Poetry.

In a `pyproject.toml` file where Poetry is used, _deptry_ will extract:

- regular dependencies from entries under `[tool.poetry.dependencies]` section
- development dependencies from entries under each `[tool.poetry.group.<group>.dependencies]` section (or the
  legacy `[tool.poetry.dev-dependencies]` section)

For instance, given the following `pyproject.toml` file:

```toml title="pyproject.toml"
[tool.poetry.dependencies]
python = "^3.10"
orjson = "^3.0.0"
click = { version = "^8.0.0", optional = true }

[tool.poetry.extras]
cli = ["click"]

[tool.poetry.group.docs.dependencies]
mkdocs = "1.6.1"

[tool.poetry.group.test.dependencies]
pytest = "8.3.3"
pytest-cov = "5.0.0"
```

the following dependencies will be extracted:

- regular dependencies: `orjson`, `click`
- development dependencies: `mkdocs`, `pytest`, `pytest-cov`

## `requirements.txt` (pip, pip-tools)

_deptry_ supports extracting [dependencies using
`requirements.txt` format](https://pip.pypa.io/en/stable/reference/requirements-file-format/), which is mostly used
by [pip](https://pip.pypa.io/en/stable/) and [pip-tools](https://pip-tools.readthedocs.io/en/stable/).

By default, _deptry_ will look for:

- regular dependencies in `requirements.txt` (or `requirements.in` if existing, assuming pip-tools is used)
- development dependencies in `dev-requirements.txt` and `requirements-dev.txt`

For instance, given the following `requirements.txt` file:

```python title="requirements.txt"
click>=8.0.0
orjson>=3.0.0
```

and the following `dev-requirements.txt` file:

```python title="dev-requirements.txt"
mkdocs==1.6.1
pytest==8.3.3
pytest-cov==5.0.0
```

the following dependencies will be extracted:

- regular dependencies: `click`, `orjson`
- development dependencies: `mkdocs`, `pytest`, `pytest-cov`

If a requirements
file [references other requirements files](https://pip.pypa.io/en/stable/reference/requirements-file-format/#referring-to-other-requirements-files),
for instance with `-r other-requirements.txt`, _deptry_ will also include the dependencies from the referenced files.

!!! note

    If using different files for regular dependencies, [`--requirements-files`](usage.md#requirements-files) (or its
    `requirements_files` equivalent in `pyproject.toml`) can be used to instruct _deptry_ about the requirements files
    locations. Similarly, [`--requirements-files-dev`](usage.md#requirements-files-dev) (or its `requirements_files_dev`
    equivalent in `pyproject.toml`) can be used for requirements files containing development dependencies.
