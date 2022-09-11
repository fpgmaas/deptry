# Configuration with pyproject.toml

## Configuration

_deptry_ can be configured by adding a `[tool.deptry]` section to _pyproject.toml_. The possible arguments are:

- `exclude`: `List`
- `ignore_notebooks`: `bool`
- `ignore_obsolete`: `List`
- `ignore_missing`: `List`
- `ignore_misplaced_dev`: `List`
- `ignore_transitive`: `List`
- `skip_obsolete`: `bool`
- `skip_missing`: `bool`
- `skip_transitive`: `bool`
- `skip_misplaced_dev`: `bool`
- `requirements_txt`: `str`
- `requirements_txt_dev`: `List`

Note that the command line arguments that should be passed as a string with comma-separated values should simply be passed as a list in _pyproject.toml_.

An example of a configuration section for _deptry_ is given below.

```
[tool.deptry]
exclude = [
  'venv','.venv','tests','setup.py','docs'
]
ignore_obsolete = [
  'alpha',
  'beta'
]
ignore_transitive = [
  'gamma'
]
skip_missing = true
```

For an explanation of the arguments run `deptry --help` or see [Usage and Configuration](./usage.md).

## Lookup hierarchy

Command-line options have defaults that you can see with `deptry --help`. A _pyproject.toml_ can override those defaults. Finally, options provided by the user on the command line override both.