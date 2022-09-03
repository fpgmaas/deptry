Dependencies are:

```
pandas
numpy
toml
cookiecutter-poetry
isort
click
```

Imported in .py files are

```
pandas
numpy
click
```

Additional imports in .ipynb file:

```
cookiecutter_poetry
```

pyproject.toml specifies to ignore the dependency:

```
toml
```

So expected output for obsolete packages when ignoring ipynb: 

```
cookiecutter-poetry
isort
```
Expected output for obsolete packages when including ipynb files: 

```
isort
```
