## Dependencies

Dependencies are:

```
toml
urllib3
isort
click
requests
pkginfo
```

dev-dependencies:

```
black
```

## Imports

Imported in .py files are

```
click
urllib3
black
white
```

Additional imports in .ipynb file:

```
toml
```

## Config

pyproject.toml specifies to ignore the dependencies (one through `ignore_unused`, and one through the to-be
deprecated `ignore_obsolete`):

```
pkginfo
requests
```

## Output

So expected output without any additional configuration:

```
unused: isort
missing: white
transitive: None
dev: black
```
