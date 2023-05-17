Given https://github.com/fpgmaas/deptry/issues/398, it might make sense to implement this similar to `ruff` as well. `ruff` has the following flags:

```
  --ignore <RULE_CODE>
      Comma-separated list of rule codes to disable
  --per-file-ignores <PER_FILE_IGNORES>
      List of mappings from file pattern to code to exclude
```

In our case, we could have the following flags:

```
--ignore
--per-rule-ignores
--per-file-ignores
```

`--ignore` can be used to ignore a rule (DEP001, DEP002, etc) in the entire codebase. e.g.

```shell
deptry . --ignore DEP001,DEP002
```

`--per-rule-ignores` can be used to skip certain packages or modules for specific rules, e.g: Ignore `matplotlib` for `DEP002`.


```shell
deptry . --per-rule-ignores DEP001=matplotlib,DEP002=pandas|numpy
```

The `--per-file-ignores` can be used to skip checking for specific rules for specific files. Here, we might want to give functionality to both ignore a rule completely per file, and only ignore it for specific modules/dependencies:

```shell
deptry . --per-file-ignores DEP001=path/to/file1.py,DEP002=path/to/file2.py:pandas|numpy
```

This would ignore `DEP001` completely in `file1.py`, and it would ignore `pandas` and `numpy` for `DEP002` in `file2.py`.
