Dependencies are:

```
toml
urllib3
isort
click
requests
pkginfo
```

Imported in .py files are

```
click
requests
urllib3
```

Additional imports in .ipynb file:

```
toml
```

pyproject.toml specifies to ignore the dependency:

```
pkginfo
```

So expected output for obsolete packages when ignoring ipynb: 

```
isort
toml
```
Expected output for obsolete packages when including ipynb files: 

```
isort
```
