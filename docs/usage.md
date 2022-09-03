# Usage & Configuration

## Prerequisites

In order to check for obsolete imports, _deptry_ should be run directly within the directory that contains the _pyproject.toml_ file, and it requires the environment created with _pyproject.toml_ to be activated.

## Basic Usage

_deptry_ can be run with

```sh
deptry check .
```

which might output the following:

```
pyproject.toml contains obsolete dependencies: ['pandas', 'numpy']
```

## Increased verbosity

To show more details about the scanned python files, the imported modules found, and how deptry determined which dependencies are obsolete, add the `-v` flag:

```sh
deptry check . -v
```

## Ignore dependencies

Sometimes, you might want _deptry_ to ignore certain dependencies, for example when you have an module that is used but not imported, or when _deptry_
incorrectly marks a dependency as obsolete. Dependencies can be ignore with the `-i` flag:

```sh
deptry check . -i pandas
```

Multiple dependencies can be ignored by using the flag multiple times:

```sh
deptry check . -i pandas -i numpy
```

## Ignore directories

_deptry_ scans the working directory and it's subdirectories recursively for `.py` and `.ipynb` files to scan for import statements. By default,
the `.venv` directory is ignored. To ignore other directories, use the `-id` flag. Note that this overwrites the default, so to ignore
both the `.venv` directory and another directory, use the flag twice:

```sh
deptry check . -id .venv -id other_directory
```

## Ignore notebooks

By default, _deptry_ scans the working directory for `.py` and `.ipynb` files to check for import statements. To ignore `.ipynb` files, use the `--ignore-notebooks` flag:

```sh
deptry check . --ignore-notebooks
```

## pyproject.toml

_deptry_ can also be configured through `pyproject.toml`. An example `pyproject.toml` entry for `deptry` looks as follows:

```toml
[tool.deptry]
ignore_dependencies = [
'pandas'
]
ignore_directories = [
'.venv',
'other_directory'
]
ignore_notebooks = false
```

## Lookup hierarchy

Command-line options have defaults that you can see in --help. A pyproject.toml can override those defaults. Finally, options provided by the user on the command line override both.