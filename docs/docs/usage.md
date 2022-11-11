# Usage & Configuration

## Configuration

_deptry_ can be configured with command line arguments or by adding a `[tool.deptry]` section to _pyproject.toml_. Explanation for the command line arguments can
be obtained by running `deptry --help`, and examples are given below. For configuration using _pyproject.toml_, see [Configuration with pyproject.toml](./pyproject-toml.md)


## Basic Usage

_deptry_ can be run with

```sh
deptry .
```

Where `.` is the path to the root directory of the project to be scanned. All other arguments should be specified relative to this directory.

## Dependencies extraction

To determine the project's dependencies, _deptry_ will scan the root directory for files in the following order:

- If a `pyproject.toml` file with a `[tool.poetry.dependencies]` section is found, _deptry_ will assume it uses Poetry and extract:
  - dependencies from `[tool.poetry.dependencies]` section
  - development dependencies from `[tool.poetry.group.dev.dependencies]` or `[tool.poetry.dev-dependencies]` section
- If a `pyproject.toml` file with a `[tool.pdm.dev-dependencies]` section is found, _deptry_ will assume it uses PDM and extract:
  - dependencies from `[project.dependencies]` and `[project.optional-dependencies]` sections
  - development dependencies from `[tool.pdm.dev-dependencies]` section.
- If a `pyproject.toml` file with a `[project]` section is found, _deptry_ will assume it uses [PEP 621](https://peps.python.org/pep-0621/) for dependency specification and extract:
  - dependencies from `[project.dependencies]` and `[project.optional-dependencies]` sections
- If a `requirements.txt` file is found, _deptry_ will extract:
  - dependencies from it
  - development dependencies from `dev-dependencies.txt` and `dependencies-dev.txt`, if any exist

_deptry_ can also be configured to look for `requirements.txt` files with other names or in other directories. See [requirements.txt files](#requirementstxt-files).

## Excluding files and directories

To determine issues with imported modules and dependencies, _deptry_ will scan the working directory and its subdirectories recursively for `.py` and `.ipynb` files, so it can
extract the imported modules from those files. Any files solely used for development purposes, such as files used for unit testing, should not be scanned. By default, the directories
`venv`, `.venv`, `tests`,`.git` and the file `setup.py` are excluded.

To ignore other directories and files than the defaults, use the `--exclude` (or `-e`) flag. The argument can either be one long regular expression, or it can be reused multiple times to pass multiple smaller regular expressions. The paths should be specified as paths relative to the directory _deptry_ is running in, without the trailing `./`. An example:

```sh
deptry . -e bar -e ".*/foo/"
deptry . --exclude "bar|.*/foo/"
```

The two statements above are equivalent, and will both ignore all files in the directory `bar`, and all files within any directory named `foo`.

Note that using the `--exclude` argument overwrites the defaults. To add additional patterns to ignore
on top of the defaults instead of overwriting them, use the `--extend-exclude` (or `-ee`) flag.

```sh
deptry . -ee bar -ee ".*/foo/"
deptry . --extend-exclude "bar|.*/foo/"
```

This will exclude `venv`, `.venv`, `.git`, `tests`, `setup.py`, `bar`, and any directory named `foo`.

## Increased verbosity

To show more details about the scanned python files, the imported modules found, and how deptry determined which dependencies are obsolete, add the `-v` flag:

```sh
deptry . -v
```

## Skip checks for obsolete, transitive or misplaced development dependencies.

Checks for obsolete, transitive, missing, or misplaced development dependencies can be skipped by using the corresponding flags:

```sh
deptry . --skip-obsolete
deptry . --skip-transitive
deptry . --skip-missing
deptry . --skip-misplaced-dev
```

## Ignore dependencies

Sometimes, you might want _deptry_ to ignore certain dependencies in certain checks, for example when you have an module that is used but not imported.
Dependencies or modules can be ignored for each check separately with the `--ignore-obsolete`, `--ignore-transitive`, `--ignore-missing` or `--ignore-misplaced-dev` flag, or with their
respective abbreviations `-io`, `-it`, `-im` and `-id`. Multiple elements can be passed to the argument by providing a comma-separated list.

For example, the following will ignore dependency foo while checking for obsolete dependencies and
will ignore module bar while checking for missing dependencies

```sh
deptry . --ignore-obsolete foo --ignore-missing bar
```

The following  will ignore both foo and bar while checking for obsolete dependencies

```sh
deptry . --ignore-obsolete foo,bar
```

## Ignore notebooks

By default, _deptry_ scans the working directory for `.py` and `.ipynb` files to check for import statements. To ignore `.ipynb` files, use the `--ignore-notebooks` flag:

```sh
deptry . --ignore-notebooks
```

## requirements.txt files

_deptry_ can be configured to extract dependencies from [pip](https://pip.pypa.io/en/stable/user_guide/) requirements files other than `requirements.txt`. Similarly
it can also be configured to extract development dependencies from other files than `dev-requirements.txt` and `requirements-dev.txt`. For this, use the `--requirements-txt` and
`--requirements-txt-dev` arguments. For example:

```
deptry . \
    --requirements-txt req/prod.txt \
    --requirements-txt-dev req/dev.txt,req/test.txt
```

Multiple files can be passed to both `requirements-txt` and `requirements-txt-dev` by using a comma-separated list.

## Output as a json file

_deptry_ can be configured to write the detected issues to a json file by specifying the `--json-output` (`-o`) flag. For example:

```
deptry . -o deptry.json
```

An example of the contents of the resulting `deptry.json` file is as follows:

```
{
    "obsolete": [
        "foo"
    ],
    "missing": [],
    "transitive": [],
    "misplaced_dev": []
}
```

## usage in pre-commit

_deptry_ can be added to your [pre-commit](https://pre-commit.com/) rules.  Here is
an example config for your .pre-commit-config.yaml file:

```
-   repo: https://github.com/fpgmaas/deptry.git
    rev: <tag>
    hooks:
    - id: deptry
      args:
        - "--skip-missing"
```

Replace `<tag>` with one of the [tags](https://github.com/fpgmaas/deptry/tags) from the
project or a specific commit hash.

!!! important

    This will only pull in the pre commit-hooks config file from the version passed to the `rev` agument.  The actual version of deptry that will be run will be the first one found in your path, so you will need to add deptry to your local virtual environment for the pre-commit.

    For the pre-commit hook to run successfully, it should be run within the virtual environment of the project to be scanned, since it needs access to the metadata of the installed packages.
