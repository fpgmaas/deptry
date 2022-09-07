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

## Increased verbosity

To show more details about the scanned python files, the imported modules found, and how deptry determined which dependencies are obsolete, add the `-v` flag:

```sh
deptry . -v
```

## Ignore directories

_deptry_ scans the working directory and it's subdirectories recursively for `.py` and `.ipynb` files to scan for import statements. By default,
the `.venv` directory is ignored. To ignore other directories, use the `-id` flag. Note that this overwrites the default, so to ignore
both the `.venv` directory and another directory, use the flag twice:

```sh
deptry . -id .venv -id other_directory
```

## Skip checks for obsolete, transitive or missing dependencies.

Checks for obsolete, transitive or missing dependencies can be skipped by using the corresponding flags:

```sh
deptry . --skip-obsolete
deptry . --skip-transitive
deptry . --skip-missing
```

## Ignore dependencies

Sometimes, you might want _deptry_ to ignore certain dependencies in certain checks, for example when you have an module that is used but not imported. 
Dependencies can be ignored for each check separately with the `--ignore-obsolete`, `--ignore-transitive`, or `--ignore-missing` flag, or with their 
respective abbreviations `-io`, `-it`, `-im`. Each argument can be used multiple times to ignore multiple dependencies. Some examples:

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