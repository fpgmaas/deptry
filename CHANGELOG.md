# Changelog

## 0.13.0 - 2024-03-12

### Features

* _deptry_ will now report invalid configuration options defined in `pyproject.toml` ([#571](https://github.com/fpgmaas/deptry/pull/571))

### Bug Fixes

* Stricten URL detection to avoid flagging libraries like `httpx` as URLs ([#570](https://github.com/fpgmaas/deptry/pull/570))

### Full Changelog

https://github.com/fpgmaas/deptry/compare/0.12.0...0.13.0


## 0.12.0 - 2023-06-18

This release introduces a significant change to the command-line flags and configuration options to make use of the error codes introduced in release [0.10.0](https://github.com/fpgmaas/deptry/releases/tag/0.10.0).

| Code   | Issue                            |
|--------|----------------------------------|
| DEP001 | Missing dependency               |
| DEP002 | Unused/obsolete dependency       |
| DEP003 | Transitive dependency            |
| DEP004 | Misplaced development dependency |

### Features

* **Replaced --skip-unused, --skip-obsolete, --skip-missing, --skip-misplaced-dev flags**: We have replaced the currently existing flags with the more generalized `--ignore` flag. Now, instead of skipping types of checks, you can specify the exact error codes to ignore using the `--ignore` flag (e.g., `deptry . --ignore "DEP001,DEP002"` to ignore checking for missing and unused dependencies).

The changes are also reflected in `pyproject.toml`. For example,


```toml
[tool.deptry]
skip_missing = true
skip_unused = true
```

is superseded by

```toml
[tool.deptry]
ignore = ["DEP001", "DEP002"]
```

* **Replaced --ignore-unused, --ignore-obsolete, --ignore-missing, --ignore-misplaced-dev flags**: Previously, specific checks for spefific dependencies/modules could be ingored using the `--ignore-<code>` flags. We are replacing these flags with the more generalized `--per-rule-ignores` flag. This flag allows you to specify dependencies that should be ignored for specific error codes, offering granular control over which errors are ignored for which dependencies. For instance, `deptry . --per-rule-ignores DEP001=matplotlib,DEP002=pandas|numpy` means `DEP001` will be ignored for `matplotlib`, while `DEP002` will be ignored for both `pandas` and `numpy`.

The changes are also reflected in `pyproject.toml`. For example,

```toml
[tool.deptry]
ignore_missing = ["matplotlib"]
ignore_unused = ["pandas", "numpy"]
```

is superseded by

```toml
[tool.deptry.per_rule_ignores]
DEP001 = ["matplotlib"]
DEP002 = ["pandas", "numpy"]
```

Please note that while the legacy arguments are still functional as of Deptry 0.12.0, we do plan to remove them in a future 1.0.0 release.


* Consider all groups for dev dependencies ([#392](https://github.com/fpgmaas/deptry/pull/392))

### Bug Fixes

* Handle `SyntaxError` raised by `ast.parse` ([#426](https://github.com/fpgmaas/deptry/pull/426))

### Full Changelog

https://github.com/fpgmaas/deptry/compare/0.11.0...0.12.0


## 0.11.0 - 2023-05-10

### Deprecations

* `--skip-obsolete` CLI option and its `skip_obsolete` couterpart in `pyproject.toml` are being replaced with `--skip-unused` and `skip_unused`, respectively
* `--ignore-obsolete` CLI option and its `ignore_obsolete` counterpart in `pyproject.toml` are being replaced with `--ignore-unused` and `ignore_unused`, respectively

This is done to account for a wording change, as we are replacing "obsolete" with "unused", since it has a clearer meaning for users.

The legacy options will still be usable for the time being, with a warning being shown in the terminal, but they will be removed in a future release, so you are advised to migrate to the new ones.

### Features

* Add ability to pass multiple source directories ([#381](https://github.com/fpgmaas/deptry/pull/381))
* Replace the word `obsolete` with `unused` ([#373](https://github.com/fpgmaas/deptry/pull/373))

### Bug Fixes

* Load gitignore from where CLI is invoked ([#380](https://github.com/fpgmaas/deptry/pull/380))

### Full Changelog

https://github.com/fpgmaas/deptry/compare/0.10.1...0.11.0


## 0.10.1 - 2023-05-09

### Bug Fixes

* Fix terminal output when only a single file is scanned ([#372](https://github.com/fpgmaas/deptry/pull/372))
* Fix issue with `DEP004` being raised incorrectly when a dependency is defined both as a dev one and non-dev one ([#376](https://github.com/fpgmaas/deptry/pull/376))

### Full Changelog

[0.10.0...0.10.1](https://github.com/fpgmaas/deptry/compare/0.10.0...0.10.1)


## 0.10.0 - 2023-05-08

### Breaking Changes

Release `0.10.0` of deptry brings a significant improvement to the way in which issues are reported. Previously, issues were reported in a summarized format, making it difficult for users to pinpoint exactly where in the code the issue was occurring. This is resolved by https://github.com/fpgmaas/deptry/pull/357, which adds location information to the detected issues.

https://github.com/fpgmaas/deptry/pull/367 adds error codes to identify the different issue types:

| Code   | Issue                            |
|--------|----------------------------------|
| DEP001 | Missing dependency               |
| DEP002 | Obsolete dependency              |
| DEP003 | Transitive dependency            |
| DEP004 | Misplaced development dependency |

Here's an example of how issues are now reported in release 0.10.0:

```console
foo/bar.py:11:11: DEP002 'an_import' imported but missing from the dependencies
foo/bar.py:12:11: DEP002 'another_import' imported but missing from the dependencies
foo/baz.py:13:11: DEP003 'cfgv' imported but it is a transitive dependency
pyproject.toml: DEP001 'pandas' defined as a dependency but not used in the codebase
```

The json output generated by using the `-o` or `--json-output` is also modified to include the new error codes and location information:

```json
{
  "error": {
    "code": "DEP001",
    "message": "'seven' imported but missing from the dependency definitions"
  },
  "module": "seven",
  "location": {
    "file": "foo/bar.py",
    "line": 2,
    "column": 0
  }
}
```

### Features

* Add location to error reports by ([#357](https://github.com/fpgmaas/deptry/pull/357))
* Add colours to text output by ([#368](https://github.com/fpgmaas/deptry/pull/368))

### Full Changelog

[0.9.0...0.10.0](https://github.com/fpgmaas/deptry/compare/0.9.0...0.10.0)


## 0.9.0 - 2023-05-06

### Breaking Changes

#### Python 3.7 support dropped

Support for Python 3.7 has been dropped in https://github.com/fpgmaas/deptry/pull/352, given that it will reach end of life soon, and that PyPI stats show a really low usage of it. If you are using `deptry` on Python 3.7, consider upgrading to 3.8, or staying on `<0.9.0`.

#### Behaviour changes in package name guessing

In case packages don't provide the Python modules they expose, `deptry` tries to guess the package name by converting `-` to `_`, as a best effort, and warns about it in the logs. Before https://github.com/fpgmaas/deptry/pull/337, `deptry` always guessed the module name, regardless of if the package provided the necessary information or not. Now, it will only guess the module name if the package does not provide the information and no mapping has been provided using the new `--package-module-name-map` flag (or `package_module_name_map` option in `pyproject.toml`).

#### Handling modules without `__init__.py`

With https://github.com/fpgmaas/deptry/pull/285, `deptry` will now consider the following things as local modules:
- directories without `__init__.py` (and at least one Python file)
- single Python files

Previously, `deptry` only considered directories as local modules if an `__init__.py` was present, and did not account for cases where a single Python file could also be a local module, alongside directories.

### Features

* Drop support for Python 3.7 ([#352](https://github.com/fpgmaas/deptry/pull/352))
* Only try to guess module associated to a dependency as a fallback for when the package doesn't provide such information ([#337](https://github.com/fpgmaas/deptry/pull/337))
* Handle local modules without `__init__.py` ([#285](https://github.com/fpgmaas/deptry/pull/285))
* Ability to configure a map of package names to module names ([#333](https://github.com/fpgmaas/deptry/pull/333))

### Bug Fixes

* Replace 'PDM' with 'poetry' in log ([#294](https://github.com/fpgmaas/deptry/pull/294))
* Account for Windows in code and tests ([#343](https://github.com/fpgmaas/deptry/pull/343))

### Miscellaneous

* Run tests on macOS and Windows on CI ([#342](https://github.com/fpgmaas/deptry/pull/342))

### Full Changelog

[0.8.0...0.9.0](https://github.com/fpgmaas/deptry/compare/0.9.0...0.10.0)


## 0.8.0 - 2023-01-24

### Features

* Don't filter out `setuptools` ([#262](https://github.com/fpgmaas/deptry/pull/262))
* Use `sys.stdlib_module_names` to get stdlibs in Python >= 3.10 ([#275](https://github.com/fpgmaas/deptry/pull/275))

### Miscellaneous

* Drop `flake8` to only use `ruff` ([#268](https://github.com/fpgmaas/deptry/pull/268))
* Use more `ruff` rules and replace `pyupgrade` and `pygrep-hooks` usages ([#276](https://github.com/fpgmaas/deptry/pull/276))

### Full Changelog

[0.7.1...0.8.0](https://github.com/fpgmaas/deptry/compare/0.7.1...0.8.0)


## 0.7.1 - 2023-01-07

### Features

* Exclude files from `.gitignore` [#248](https://github.com/fpgmaas/deptry/pull/248))
* Add support for known first party modules [#257](https://github.com/fpgmaas/deptry/pull/257))

### Full Changelog

[0.7.0...0.7.1](https://github.com/fpgmaas/deptry/compare/0.7.0...0.7.1)


## 0.7.0 - 2022-12-27

### Breaking Changes

Previously,  `deptry` always searched for a `pyproject.toml` file in the root directory passed as a positional argument to the `deptry` command. Since this is not in line with what most other tools in the ecosystem do, this is changed in release `0.7.0`.

In previous releases, when running:

```shell
deptry src
```

`deptry` would search for both a `pyproject.toml` and for Python files to scan in the `src` directory.

Since this release, when running:

```shell
deptry src
```

`deptry` will search for `pyproject.toml` in the location it is run from, and for Python files to scan in the `src` directory.

The downside of the changes outlined above, is that this could break some projects that did explicitly want to find `pyproject.toml` in a directory other than the positional argument specified as `root`. For this purpose, release `0.7.0` adds a `--config` argument that can be used to explicitly pass the location of `pyproject.toml`.

### Features

* Separate `pyproject.toml` location from `root` argument ([#244](https://github.com/fpgmaas/deptry/pull/244))
* Expose and handle `--config` argument ([#245](https://github.com/fpgmaas/deptry/pull/245))

### Miscellaneous

* Only load local modules once by ([#242](https://github.com/fpgmaas/deptry/pull/242))
* More efficient Python files retrieval ([#243](https://github.com/fpgmaas/deptry/pull/243))

### Full Changelog

[0.6.6...0.7.0](https://github.com/fpgmaas/deptry/compare/0.6.6...0.7.0)


## 0.6.6 - 2022-11-22

### Features

* Add .direnv to default exclude argument ([#197](https://github.com/fpgmaas/deptry/pull/197))
* Add logic to `NotebookImportExtractor` to guess the encoding on initial `UnicodeDecodeError` ([#216](https://github.com/fpgmaas/deptry/pull/216))

### Miscellaneous

* Decrease lower bound of `chardet` dependency to `4.0.0` ([#205](https://github.com/fpgmaas/deptry/pull/205))

### Full Changelog

[0.6.5...0.6.6](https://github.com/fpgmaas/deptry/compare/0.6.5...0.6.6)


## 0.6.5 - 2022-11-14

No user facing change.

### Full Changelog

[0.6.4...0.6.5](https://github.com/fpgmaas/deptry/compare/0.6.4...0.6.5)


## 0.6.4 - 2022-11-09

### Features

* Add support for PEP 621 ([#166](https://github.com/fpgmaas/deptry/pull/166))

### Bug Fixes

* Remove obsolete duplicated local import detection ([#172](https://github.com/fpgmaas/deptry/pull/172))

### Full Changelog

[0.6.3...0.6.4](https://github.com/fpgmaas/deptry/compare/0.6.3...0.6.4)


## 0.6.3 - 2022-10-23

### Features

* Add hook for usage with `pre-commit` ([#157](https://github.com/fpgmaas/deptry/pull/157))

### Full Changelog

[0.6.2...0.6.3](https://github.com/fpgmaas/deptry/compare/0.6.2...0.6.3)


## 0.6.2 - 2022-10-22

### Bug Fixes

* Solve issue with importing from local files ([#163](https://github.com/fpgmaas/deptry/pull/163))

### Full Changelog

[0.6.1...0.6.2](https://github.com/fpgmaas/deptry/compare/0.6.1...0.6.2)


## 0.6.1 - 2022-10-08

### Features

* Add support for PEP621 with PDM ([#155](https://github.com/fpgmaas/deptry/pull/155))

### Full Changelog

[0.5.13...0.6.1](https://github.com/fpgmaas/deptry/compare/0.5.13...0.6.1)


## 0.5.13 - 2022-10-02

### Features

* Add support for Python 3.11 ([#152](https://github.com/fpgmaas/deptry/pull/152))

### Full Changelog

[0.5.12...0.5.13](https://github.com/fpgmaas/deptry/compare/0.5.12...0.5.13)


## 0.5.12 - 2022-10-01

### Features

* Accept multiple `requirements.txt` ([#141](https://github.com/fpgmaas/deptry/pull/141))

### Full Changelog

[0.5.11...0.5.12](https://github.com/fpgmaas/deptry/compare/0.5.11...0.5.12)


## 0.5.11 - 2022-09-30

### Miscellaneous

* Remove dependency on `isort` ([#140](https://github.com/fpgmaas/deptry/pull/140))

### Full Changelog

[0.5.10...0.5.11](https://github.com/fpgmaas/deptry/compare/0.5.10...0.5.11)


## 0.5.10 - 2022-09-27

No user facing change.

### Full Changelog

[0.5.9...0.5.10](https://github.com/fpgmaas/deptry/compare/0.5.9...0.5.10)


## 0.5.9 - 2022-09-26

### Bug Fixes

* Fix issue with logging if no `[tool.deptry]` section was found in `pyproject.toml` ([#134](https://github.com/fpgmaas/deptry/pull/134))

### Full Changelog

[0.5.8...0.5.9](https://github.com/fpgmaas/deptry/compare/0.5.8...0.5.9)


## 0.5.8 - 2022-09-26

No user facing change.

### Full Changelog

[0.5.7...0.5.8](https://github.com/fpgmaas/deptry/compare/0.5.7...0.5.8)


## 0.5.7 - 2022-09-24

### Features

* Add option to write output to JSON file ([#125](https://github.com/fpgmaas/deptry/pull/125))

### Full Changelog

[0.5.6...0.5.7](https://github.com/fpgmaas/deptry/compare/0.5.6...0.5.7)


## 0.5.6 - 2022-09-22

### Miscellaneous

* Replace `toml` with `tomli`/`tomllib` for parsing TOML ([#123](https://github.com/fpgmaas/deptry/pull/123))

### Full Changelog

[0.5.5...0.5.6](https://github.com/fpgmaas/deptry/compare/0.5.5...0.5.6)


## 0.5.5 - 2022-09-20

### Miscellaneous

* Rename `DIRECTORY` argument to `ROOT` ([#121](https://github.com/fpgmaas/deptry/pull/121))

### Full Changelog

[0.5.4...0.5.5](https://github.com/fpgmaas/deptry/compare/0.5.4...0.5.5)


## 0.5.4 - 2022-09-19

### Miscellaneous

* Add a summary line to the logging ([#120](https://github.com/fpgmaas/deptry/pull/120))

### Full Changelog

[0.5.3...0.5.4](https://github.com/fpgmaas/deptry/compare/0.5.3...0.5.4)


## 0.5.3 - 2022-09-18

### Miscellaneous

* Set Python version upper range to `<4.0` ([#117](https://github.com/fpgmaas/deptry/pull/117))

### Full Changelog

[0.5.2...0.5.3](https://github.com/fpgmaas/deptry/compare/0.5.2...0.5.3)


## 0.5.2 - 2022-09-18

### Features

* Extract top level module names from `RECORD` ([#116](https://github.com/fpgmaas/deptry/pull/116))

### Full Changelog

[0.5.1...0.5.2](https://github.com/fpgmaas/deptry/compare/0.5.1...0.5.2)


## 0.5.1 - 2022-09-18

### Features

* Parse `egg=...` in urls for `requirements.txt` ([#115](https://github.com/fpgmaas/deptry/pull/115))

### Full Changelog

[0.5.0...0.5.1](https://github.com/fpgmaas/deptry/compare/0.5.0...0.5.1)


## 0.5.0 - 2022-09-17

### Features

* Support regexes for file exclusions ([#111](https://github.com/fpgmaas/deptry/pull/111))

### Full Changelog

[0.4.7...0.5.0](https://github.com/fpgmaas/deptry/compare/0.4.7...0.5.0)


## 0.4.7 - 2022-09-15

### Miscellaneous

* Only decode files if initial decoding failed ([#105](https://github.com/fpgmaas/deptry/pull/105))

### Full Changelog

[0.4.6...0.4.7](https://github.com/fpgmaas/deptry/compare/0.4.6...0.4.7)


## 0.4.6 - 2022-09-14

### Features

* Detect file encoding with `chardet` before parsing Python files ([#103](https://github.com/fpgmaas/deptry/pull/103))

### Full Changelog

[0.4.5...0.4.6](https://github.com/fpgmaas/deptry/compare/0.4.5...0.4.6)


## 0.4.5 - 2022-09-13

No user facing change.

### Full Changelog

[0.4.4...0.4.5](https://github.com/fpgmaas/deptry/compare/0.4.4...0.4.5)


## 0.4.4 - 2022-09-13

### Features

* Add support for reading dependencies form urls in `requirements.txt` ([#100](https://github.com/fpgmaas/deptry/pull/100))

### Full Changelog

[0.4.3...0.4.4](https://github.com/fpgmaas/deptry/compare/0.4.3...0.4.4)


## 0.4.3 - 2022-09-13

### Bug Fixes

* Solve an issue where missing dev dependencies were added to the list as `None` ([#99](https://github.com/fpgmaas/deptry/pull/99))

### Full Changelog

[0.4.2...0.4.3](https://github.com/fpgmaas/deptry/compare/0.4.2...0.4.3)


## 0.4.2 - 2022-09-12

### Features

* Add a warning to not install `deptry` globally, but within virtual environment ([#]())

### Bug Fixes

* Fix an issue with `requirements.txt` not being found if not in root dir ([#94](https://github.com/fpgmaas/deptry/pull/94))

### Full Changelog

[0.4.1...0.4.2](https://github.com/fpgmaas/deptry/compare/0.4.1...0.4.2)


## 0.4.1 - 2022-09-11

### Features

* Ignore `setuptools` and `setup.py` by default ([#88](https://github.com/fpgmaas/deptry/pull/88))

### Full Changelog

[0.4.0...0.4.1](https://github.com/fpgmaas/deptry/compare/0.4.0...0.4.1)


## 0.4.0 - 2022-09-11

### Features

* Add support for `requirements.txt` ([#87](https://github.com/fpgmaas/deptry/pull/87))

### Full Changelog

[0.3.2...0.4.0](https://github.com/fpgmaas/deptry/compare/0.3.2...0.4.0)


## 0.3.2 - 2022-09-10

No user facing change.

### Full Changelog

[0.3.1...0.3.2](https://github.com/fpgmaas/deptry/compare/0.3.1...0.3.2)


## 0.3.1 - 2022-09-10

### Features

* Use commas to separate items in CLI arguments ([#87](https://github.com/fpgmaas/deptry/pull/87))

### Full Changelog

[0.2.16...0.3.1](https://github.com/fpgmaas/deptry/compare/0.2.16...0.3.1)


## 0.2.17 - 2022-09-10

### Features

* Add `--extend-exclude` option ([#76](https://github.com/fpgmaas/deptry/pull/76))

### Full Changelog

[0.2.16...0.2.17](https://github.com/fpgmaas/deptry/compare/0.2.16...0.2.17)


## 0.2.16 - 2022-09-09

No user facing change.

### Full Changelog

[0.2.15...0.2.16](https://github.com/fpgmaas/deptry/compare/0.2.15...0.2.16)


## 0.2.15 - 2022-09-09

### Features

* Guess top level name of modules by replacing `-` with `_` ([#73](https://github.com/fpgmaas/deptry/pull/73))

### Full Changelog

[0.2.14...0.2.15](https://github.com/fpgmaas/deptry/compare/0.2.14...0.2.15)


## 0.2.14 - 2022-09-09

### Features

* Handle conditional dependencies ([#65](https://github.com/fpgmaas/deptry/pull/65))

### Miscellaneous

* Decrease lower bound of `click` dependency to `8.0.0` ([#205](https://github.com/fpgmaas/deptry/pull/205))

### Full Changelog

[0.2.13...0.2.14](https://github.com/fpgmaas/deptry/compare/0.2.13...0.2.14)


## 0.2.13 - 2022-09-09

No user facing change.

### Full Changelog

[0.2.12...0.2.13](https://github.com/fpgmaas/deptry/compare/0.2.12...0.2.13)


## 0.2.12 - 2022-09-09

No user facing change.

### Full Changelog

[0.2.11...0.2.12](https://github.com/fpgmaas/deptry/compare/0.2.11...0.2.12)


## 0.2.11 - 2022-09-09

No user facing change.

### Full Changelog

[0.2.10...0.2.11](https://github.com/fpgmaas/deptry/compare/0.2.10...0.2.11)


## 0.2.10 - 2022-09-08

No user facing change.

### Full Changelog

[0.2.9...0.2.10](https://github.com/fpgmaas/deptry/compare/0.2.9...0.2.10)


## 0.2.9 - 2022-09-08

### Bug Fixes

* Fix issue with relative imports ([#54](https://github.com/fpgmaas/deptry/pull/54))

### Full Changelog

[0.2.8...0.2.9](https://github.com/fpgmaas/deptry/compare/0.2.8...0.2.9)


## 0.2.8 - 2022-09-08

### Features

* Add check for misplaced development dependencies ([#51](https://github.com/fpgmaas/deptry/pull/51))

### Full Changelog

[0.2.7...0.2.8](https://github.com/fpgmaas/deptry/compare/0.2.7...0.2.8)


## 0.2.7 - 2022-09-07

No user facing change.

### Full Changelog

[0.2.6...0.2.7](https://github.com/fpgmaas/deptry/compare/0.2.6...0.2.7)


## 0.2.6 - 2022-09-07

### Features

* Add `--version` argument to the CLI to display `deptry`'s version ([#47](https://github.com/fpgmaas/deptry/pull/47))

### Full Changelog

[0.2.5...0.2.6](https://github.com/fpgmaas/deptry/compare/0.2.5...0.2.6)


## 0.2.5 - 2022-09-07

### Features

* Add check for missing and transitive dependencies ([#43](https://github.com/fpgmaas/deptry/pull/43))

### Full Changelog

[0.2.3...0.2.5](https://github.com/fpgmaas/deptry/compare/0.2.3...0.2.5)


## 0.2.3 - 2022-09-06

No user facing change.

### Full Changelog

[0.2.2...0.2.3](https://github.com/fpgmaas/deptry/compare/0.2.2...0.2.3)


## 0.2.2 - 2022-09-06

### Full Changelog

[0.2.1...0.2.2](https://github.com/fpgmaas/deptry/compare/0.2.1...0.2.2)


## 0.2.1 - 2022-09-05

### Full Changelog

[0.2.0...0.2.1](https://github.com/fpgmaas/deptry/compare/0.2.0...0.2.1)


## 0.2.0 - 2022-09-05

### Features

* Add support for Python 3.7 ([#27](https://github.com/fpgmaas/deptry/pull/27))

### Full Changelog

[0.1.5...0.2.0](https://github.com/fpgmaas/deptry/compare/0.1.5...0.2.0)


## 0.1.5 - 2022-09-04

### Miscellaneous

* Improve logging statements ([#25](https://github.com/fpgmaas/deptry/pull/25))

### Full Changelog

[0.1.4...0.1.5](https://github.com/fpgmaas/deptry/compare/0.1.4...0.1.5)


## 0.1.4 - 2022-09-04

### Miscellaneous

* Improve logging when package name is not found ([#25](https://github.com/fpgmaas/deptry/pull/25))

### Full Changelog

[0.1.3...0.1.4](https://github.com/fpgmaas/deptry/compare/0.1.3...0.1.4)


## 0.1.3 - 2022-09-04

### Features

* Parse imports within `if`/`else` statements ([#23](https://github.com/fpgmaas/deptry/pull/23))

### Full Changelog

[0.1.2...0.1.3](https://github.com/fpgmaas/deptry/compare/0.1.2...0.1.3)


## 0.1.2 - 2022-09-04

No use facing change.

### Full Changelog

[0.1.1...0.1.2](https://github.com/fpgmaas/deptry/compare/0.1.1...0.1.2)


## 0.1.1 - 2022-09-04

### Features

* Replace `deptry check` command with `deptry` ([#21](https://github.com/fpgmaas/deptry/pull/21))

### Full Changelog

[0.0.4...0.1.1](https://github.com/fpgmaas/deptry/compare/0.0.4...0.1.1)


## 0.0.4 - 2022-09-03

### Features

* Add ability to specify the root directory ([#13](https://github.com/fpgmaas/deptry/pull/13))

### Full Changelog

[0.0.3...0.0.4](https://github.com/fpgmaas/deptry/compare/0.0.3...0.0.4)


## 0.0.3 - 2022-09-03

### Features

* Add support for Jupyter Notebooks ([#11](https://github.com/fpgmaas/deptry/pull/11))

### Full Changelog

[0.0.2...0.0.3](https://github.com/fpgmaas/deptry/compare/0.0.2...0.0.3)


## 0.0.2 - 2022-09-02

### Features

* Add mapping for common packages without metadata ([#1](https://github.com/fpgmaas/deptry/pull/1))

### Full Changelog

[0.0.1...0.0.2](https://github.com/fpgmaas/deptry/compare/0.0.1...0.0.2)


## 0.0.1 - 2022-09-02

Initial release
