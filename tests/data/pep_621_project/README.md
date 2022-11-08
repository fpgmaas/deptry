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

pyproject.toml specifies to ignore the dependency:

```
pkginfo
```

## Output

So expected output without any additional configuration:

```
obsolete: isort, requests (pkginfo is ignored)
missing: white
transitive: black
dev: None
```
