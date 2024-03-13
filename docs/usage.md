# Usage & Configuration

## Basic Usage

_deptry_ can be run with:

```shell
deptry .
```

where `.` is the path to the root directory of the project to be scanned.

If your project has multiple source directories, multiple root directories can be provided:

```shell
deptry a_directory another_directory
```

If you want to configure _deptry_ using `pyproject.toml`, or if your dependencies are stored in `pyproject.toml`, but it is located in another location than the one _deptry_ is run from, you can specify the location to it by using `--config <path_to_pyproject.toml>` argument.

## Dependencies extraction

To determine the project's dependencies, _deptry_ will scan the directory it is run from for files in the following order:

1. If a `pyproject.toml` file with a `[tool.poetry.dependencies]` section is found, _deptry_ will assume it uses Poetry and extract:
    - dependencies from `[tool.poetry.dependencies]` section
    - development dependencies from `[tool.poetry.group.dev.dependencies]` or `[tool.poetry.dev-dependencies]` section
2. If a `pyproject.toml` file with a `[tool.pdm.dev-dependencies]` section is found, _deptry_ will assume it uses PDM and extract:
    - dependencies from `[project.dependencies]` and `[project.optional-dependencies]` sections
    - development dependencies from `[tool.pdm.dev-dependencies]` section.
3. If a `pyproject.toml` file with a `[project]` section is found, _deptry_ will assume it uses [PEP 621](https://peps.python.org/pep-0621/) for dependency specification and extract:
    - dependencies from `[project.dependencies]` and `[project.optional-dependencies]` sections
4. If a `requirements.txt` file is found, _deptry_ will extract:
    - dependencies from it
    - development dependencies from `dev-dependencies.txt` and `dependencies-dev.txt`, if any exist

_deptry_ can be configured to look for `pip` requirements files with other names or in other directories.
See [Requirements txt](#requirements-txt) and [Requirements txt dev](#requirements-txt-dev).

## Excluding files and directories

To determine issues with imported modules and dependencies, _deptry_ will scan the working directory and its subdirectories recursively for `.py` and `.ipynb` files, so it can
extract the imported modules from those files. Any file solely used for development purposes, such as a file used for unit testing, should not be scanned. By default, the directories
`venv`, `.venv`, `.direnv`, `tests`, `.git` and the file `setup.py` are excluded.

_deptry_ also reads entries in `.gitignore` file, to ignore any pattern present in the file, similarly to what `git` does.

To ignore other directories and files than the defaults, use the `--exclude` (short `-e`) flag. The argument can either be one long regular expression, or it can be reused multiple times to pass multiple smaller regular expressions. The paths should be specified as paths relative to the directory _deptry_ is running in, without the trailing `./`. An example:

```shell
deptry . --exclude bar --exclude ".*/foo/"
deptry . --exclude "bar|.*/foo/"
```

The two statements above are equivalent, and will both ignore all files in the directory `bar`, and all files within any directory named `foo`.

Note that using the `--exclude` argument overwrites the defaults, and will prevent _deptry_ from considering entries in
`.gitignore`.
To add additional patterns to ignore on top of the defaults instead of overwriting them, or to make sure that _deptry_
still considers `.gitignore`, use the `--extend-exclude` (short `-ee`) flag.

```shell
deptry . --extend-exclude bar --extend-exclude ".*/foo/"
deptry . --extend-exclude "bar|.*/foo/"
```

This will exclude `venv`, `.venv`, `.direnv`, `.git`, `tests`, `setup.py`, `bar`, and any directory named `foo`, as well
as entries in `.gitignore`, if there are some.

## Usage in pre-commit

_deptry_ can be added to your [pre-commit](https://pre-commit.com/) rules. Here is
an example config for your `.pre-commit-config.yaml` file:

```yaml
- repo: https://github.com/fpgmaas/deptry.git
  rev: "<tag>"
  hooks:
    - id: deptry
      args: ["--ignore", "DEP001"]
```

Replace `<tag>` with one of the [tags](https://github.com/fpgmaas/deptry/tags) from the
project or a specific commit hash.

!!! important

    This will only pull in the pre commit-hooks config file from the version passed to the `rev` agument. The actual version of _deptry_ that will be run will be the first one found in your path, so you will need to add _deptry_ to your local virtual environment.

    For the pre-commit hook to run successfully, it should be run within the virtual environment of the project to be scanned, since it needs access to the metadata of the installed packages.

## Increasing verbosity

To show more details about the scanned Python files, the imported modules found, and how _deptry_ determines issues in dependencies, add the `--verbose` (short `-v`) flag:

```shell
deptry . --verbose
```

## Configuration

_deptry_ can be configured with command line arguments or by adding a `[tool.deptry]` section to `pyproject.toml`.

### Lookup hierarchy

The lookup hierarchy for each configuration option is as follows:

1. Default value is used
2. If set, value in `[tool.deptry]` section of `pyproject.toml` is used, overriding the default
3. If set, value passed through the CLI is used, overriding both the default and `pyproject.toml` values

### Options

#### Config

Path to the `pyproject.toml` file that holds _deptry_'s configuration and dependencies definition (if any).

- Type: `Path`
- Default: `pyproject.toml`
- CLI option name: `--config`
- CLI example:
```shell
deptry . --config sub_directory/pyproject.toml
```

#### No ANSI

Disable ANSI characters in terminal output.

- Type: `bool`
- Default: `False`
- CLI option name: `--no-ansi`
- CLI example:
```shell
deptry . --no-ansi
```

#### Exclude

List of patterns to exclude when searching for source files.

- Type: `List[str]`
- Default: `["venv", "\.venv", "\.direnv", "tests", "\.git", "setup\.py"]`
- `pyproject.toml` option name: `exclude`
- CLI option name: `--exclude` (short: `-e`)
- `pyproject.toml` example:
```toml
[tool.deptry]
exclude = ["a_directory", "a_python_file\\.py", "a_pattern/.*"]
```
- CLI example:
```shell
deptry . --exclude "a_directory|a_python_file\.py|a_pattern/.*"
```

#### Extend exclude

Additional list of patterns to exclude when searching for source files.
This extends the patterns set in [Exclude](#exclude), to allow defining patterns while keeping the default list.

- Type: `List[str]`
- Default: `[]`
- `pyproject.toml` option name: `extend_exclude`
- CLI option name: `--extend-exclude` (short: `-ee`)
- `pyproject.toml` example:
```toml
[tool.deptry]
extend_exclude = ["a_directory", "a_python_file\\.py", "a_pattern/.*"]
```
- CLI example:
```shell
deptry . --extend-exclude "a_directory|a_python_file\.py|a_pattern/.*"
```

#### Ignore

A comma-separated list of [rules](rules-violations.md) to ignore.

- Type: `List[str]`
- Default: `[]`
- `pyproject.toml` option name: `ignore`
- CLI option name: `--ignore` (short: `-i`)
- `pyproject.toml` example:
```toml
[tool.deptry]
ignore = ["DEP003", "DEP004"]
```
- CLI example:
```shell
deptry . --ignore DEP003,DEP004
```

#### Per rule ignores

A comma-separated mapping of packages or modules to be ignored per [rule](rules-violations.md) .

- Type: `dict[str, list[str] | str]`
- Default: `{}`
- `pyproject.toml` option name: `per_rule_ignores`
- CLI option name: `--per-rule-ignores` (short: `-pri`)
- `pyproject.toml` example:
```toml
[tool.deptry.per_rule_ignores]
DEP001 = ["matplotlib"]
DEP002 = ["pandas", "numpy"]
```
- CLI example:
```shell
deptry . --per-rule-ignores DEP001=matplotlib,DEP002=pandas|numpy
```

#### Ignore notebooks

Disable searching for notebooks (`*.ipynb`) files when looking for imports.

- Type: `bool`
- Default: `False`
- `pyproject.toml` option name: `ignore_notebooks`
- CLI option name: `--ignore-notebooks` (short: `-nb`)
- `pyproject.toml` example:
```toml
[tool.deptry]
ignore_notebooks = true
```
- CLI example:
```shell
deptry . --ignore-notebooks
```

#### Requirements txt

List of [`pip` requirements files](https://pip.pypa.io/en/stable/user_guide/#requirements-files) that contain the source dependencies.

- Type: `List[str]`
- Default: `["requirements.txt"]`
- `pyproject.toml` option name: `requirements_txt`
- CLI option name: `--requirements-txt` (short: `-rt`)
- `pyproject.toml` example:
```toml
[tool.deptry]
requirements_txt = ["requirements.txt", "requirements-private.txt"]
```
- CLI example:
```shell
deptry . --requirements-txt requirements.txt,requirements-private.txt
```

#### Requirements txt dev

List of [`pip` requirements files](https://pip.pypa.io/en/stable/user_guide/#requirements-files) that contain the source development dependencies.

- Type: `List[str]`
- Default: `["dev-requirements.txt", "requirements-dev.txt"]`
- `pyproject.toml` option name: `requirements_txt_dev`
- CLI option name: `--requirements-txt-dev` (short: `-rtd`)
- `pyproject.toml` example:
```toml
[tool.deptry]
requirements_txt_dev = ["requirements-dev.txt", "requirements-tests.txt"]
```
- CLI example:
```shell
deptry . --requirements-txt-dev requirements-dev.txt,requirements-tests.txt
```

#### Known first party

List of Python modules that should be considered as first party ones. This is useful in case _deptry_ is not able to automatically detect modules that should be considered as local ones.

- Type: `List[str]`
- Default: `[]`
- `pyproject.toml` option name: `known_first_party`
- CLI option name: `--known-first-party` (short: `-kf`)
- `pyproject.toml` example:
```toml
[tool.deptry]
known_first_party = ["bar", "foo"]
```
- CLI example:
```shell
deptry . --known-first-party bar --known-first-party foo
```

#### JSON output

Write the detected issues to a JSON file. This will write the following kind of output:

```json
[
     {
         "error": {
             "code": "DEP002",
             "message": "uvicorn defined as a dependency but not used in the codebase"
         },
         "module": "uvicorn",
         "location": {
             "file": "pyproject.toml",
             "line": null,
             "column": null
         }
     },
     {
         "error": {
             "code": "DEP002",
             "message": "uvloop defined as a dependency but not used in the codebase"
         },
         "module": "uvloop",
         "location": {
             "file": "pyproject.toml",
             "line": null,
             "column": null
         }
     },
     {
         "error": {
             "code": "DEP004",
             "message": "black imported but declared as a dev dependency"
         },
         "module": "black",
         "location": {
             "file": "src/main.py",
             "line": 4,
             "column": 0
         }
     },
     {
         "error": {
             "code": "DEP003",
             "message": "httpx imported but it is a transitive dependency"
         },
         "module": "httpx",
         "location": {
             "file": "src/main.py",
             "line": 6,
             "column": 0
         }
     }
]
```

- Type: `Path`
- Default: `None`
- `pyproject.toml` option name: `json_output`
- CLI option name: `--json-output` (short: `-o`)
- `pyproject.toml` example:
```toml
[tool.deptry]
json_output = "deptry_report.txt"
```
- CLI example:
```shell
deptry . --json-output deptry_report.txt
```

#### Package module name map

Deptry will automatically detect top level modules names that belong to a
module in two ways.
The first is by inspecting the installed packages. The second, used as fallback
for when the package is not installed, is by translating the package name to a
module name (`Foo-Bar` translates to `foo_bar`).

This however is not always sufficient. A situation may occur where a package is
not installed because it is optional and unused in the current installation.
Then when the package name doesn't directly translate to the top level module
name, or there are more top level modules names, Deptry may report both
unused packages, and missing packages. A concrete example is deptry reporting unused (optional) dependency
`foo-python`, and missing package `foo`, while package `foo-python` would
install top level module `foo`, if it were installed.

A solution is to pre-define a mapping between the pacakge name and the top
level module name(s).

* Type `dict[str, list[str] | str]`
* Default: `{}`
* `pyproject.toml` option name: `package_module_name_map`
* CLI option name: `--package-module-name-map` (short: `-pmnm`)
* `pyproject.toml` examples:
```toml
[tool.deptry.package_module_name_map]
foo-python = "foo"
```
Or for multiple top level module names:
```toml
[tool.deptry.package_module_name_map]
foo-python = [
    "foo",
    "bar",
]
```
* CLI examples:
```shell
deptry . --package-module-name-map 'foo-python=foo'
```
Multiple module names are joined by a pipe (`|`):
```shell
deptry . --package-module-name-map 'foo-python=foo|bar'
```
Multiple package name to module name mappings are joined by a comma (`,`):
```shell
deptry . --package-module-name-map 'foo-python=foo,bar-python=bar'
```
