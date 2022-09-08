# Usage & Configuration

## Prerequisites

In order to check for obsolete imports, _deptry_ requires a _pyproject.toml_ file to be present in the directory passed as the first argument, and it requires the corresponding environment to be activated.

## Configuration

_deptry_ can be configured with command line arguments or by adding a `[tool.deptry]` section to _pyproject.toml_. Explanation for the command line arguments can
be obtained by running `deptry --help`, and examples are given below. For configuration using _pyproject.toml_, see [Configuration with pyproject.toml](./pyproject-toml.md)


## Basic Usage

_deptry_ can be run with

```sh
deptry .
```

To determine issues with imported modules and dependencies, _deptry_ will scan the working directory and it's subdirectories recursively for `.py` and `.ipynb` files, so it can
extract the imported modules from those files. Any files solely used for development purposes, such as files used for unit testing, should not be scanned. By default, the directories
`.venv` and `tests` are excluded. 

## Excluding files and directories
 
To ignore other directories than the default `.venv` and `tests`, use the `--exclude` flag. Note that this overwrites the defaults, so to ignore
both the `.venv` and `tests` directories and another directory, use the flag thrice:

```sh
deptry . --exclude .venv --exclude tests --exclude other_directory
```

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
Dependencies can be ignored for each check separately with the `--ignore-obsolete`, `--ignore-transitive`, `--ignore-missing` or `--ignore-misplaced-dev` flag, or with their 
respective abbreviations `-io`, `-it`, `-im` and `-id`. Each argument can be used multiple times to ignore multiple dependencies. Some examples:

The following will ignore dependency foo while checking for obsolete dependencies and
will ignore module bar while checking for missing dependencies

```sh
deptry . --ignore-obsolete foo --ignore-missing bar
```

The following  will ignore both foo and bar while checking for obsolete dependencies

```sh
deptry . -io foo -io bar 
```

## Ignore notebooks

By default, _deptry_ scans the working directory for `.py` and `.ipynb` files to check for import statements. To ignore `.ipynb` files, use the `--ignore-notebooks` flag:

```sh
deptry . --ignore-notebooks
```