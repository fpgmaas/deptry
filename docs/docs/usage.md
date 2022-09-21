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

## pyproject.toml vs requirements.txt

To determine the project's dependencies, _deptry_ will scan the root directory for a `pyproject.toml` file with a `[tool.poetry.dependencies]` section and for a file called `requirements.txt`.

- If a `pyproject.toml` file with dependency specification is found, _deptry_ will extract both the projects dependencies and its development dependencies from there.
- If a `requirements.txt` file is found, _deptry_ will extract the project's dependencies from there, and additionally it will look for the files `dev-dependencies.txt` and `dependencies-dev.txt` to determine the project's development dependencies.
- If both a `pyproject.toml` file and `requirements.txt` are found, `pyproject.toml` takes priority, and that file is used to determine the project's dependencies.

_deptry_ can also be configured to look for a `requirements.txt` file with another name or in another directory. See [requirements.txt files](#requirementstxt-files).

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

Here, the `requirements-txt` takes only a single file as argument, but multiple files can be passed to `requirements-txt-dev` by providing them as a comma-separated list.

## usage in pre-commit

_deptry_ can be added to your [pre-commit](https://pre-commit.com/) rules.  Here is
an example config:

```
-   repo: https://github.com/fpgmaas/deptry.git
    rev: <version>
    hooks:
    - id: deptry
      args:
        - "--skip-missing"
```
