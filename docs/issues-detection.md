# Issues detection

_deptry_ looks for the following issues in dependencies:

- [Obsolete dependencies](#obsolete-dependencies)
- [Missing dependencies](#missing-dependencies)
- [Transitive dependencies](#transitive-dependencies)
- [Misplaced development dependencies](#misplaced-development-dependencies)

## Obsolete dependencies

Dependencies that are required in a project, but are not used within the codebase.

### Configuration

This check can be disabled with [Skip obsolete](usage.md#skip-obsolete) option.

Specific dependencies can be ignored with [Ignore obsolete](usage.md#ignore-obsolete) option.

### Example

On a project with the following dependencies:

```toml
[project]
dependencies = [
    "httpx==0.23.1",
    "requests==2.28.1",
]
```

and the following `main.py` that is the only Python file in the project:

```python
import httpx
import requests

def make_http_request():
    return httpx.get("https://example.com")
```

_deptry_ will report `requests` as an obsolete dependency because it is not used in the project.

To fix the issue, `requests` should be removed from `[project.dependencies]`:

```toml
[project]
dependencies = ["httpx==0.23.1"]
```

## Missing dependencies

Python modules that are imported within a project, for which no corresponding packages are found in the dependencies.

### Configuration

This check can be disabled with [Skip missing](usage.md#skip-missing) option.

Specific dependencies can be ignored with [Ignore missing](usage.md#ignore-missing) option.

### Example

On a project with the following dependencies:

```toml
[project]
dependencies = []
```

and the following `main.py` that is the only Python file in the project:

```python
import httpx

def make_http_request():
    return httpx.get("https://example.com")
```

_deptry_ will report `httpx` as a missing dependency because it is imported in the project, but not defined in the dependencies.

To fix the issue, `httpx` should be added to `[project.dependencies]`:

```toml
[project]
dependencies = ["httpx==0.23.1"]
```

## Transitive dependencies

Python modules that are imported within a project, where the corresponding dependencies are in the dependency tree, but not as direct dependencies.
For example, assume your project has a `.py` file that imports module A. However, A is not in your project's dependencies. Instead, another package (B) is in your list of dependencies, which in turn depends on A. Package A should be explicitly added to your project's list of dependencies.

### Configuration

This check can be disabled with [Skip transitive](usage.md#skip-transitive) option.

Specific dependencies can be ignored with [Ignore transitive](usage.md#ignore-transitive) option.

### Example

On a project with the following dependencies:

```toml
[project]
dependencies = [
    # Here `httpx` depends on `certifi` package.
    "httpx==0.23.1",
]
```

and the following `main.py` that is the only Python file in the project:

```python
import certifi
import httpx

def make_http_request():
    return httpx.get("https://example.com")

def get_certificates_location():
    return certifi.where()
```

_deptry_ will report `certifi` as a transitive dependency because it is not used in the project.

To fix the issue, `certifi` should be explicitly added to `[project.dependencies]`:

```toml
[project]
dependencies = [
    "httpcore==0.16.3",
    "httpx==0.23.1",
]
```

## Misplaced development dependencies

Dependencies specified as development ones that should be included as regular dependencies.

### Configuration

This check can be disabled with [Skip misplaced dev](usage.md#skip-misplaced-dev) option.

Specific dependencies can be ignored with [Ignore misplaced dev](usage.md#ignore-misplaced-dev) option.

### Example

On a project with the following dependencies:

```toml
[project]
dependencies = ["httpx==0.23.1"]

[tool.pdm.dev-dependencies]
test = [
    "orjson==3.8.3",
    "pytest==7.2.0",
]
```

And the following `main.py` that is the only Python file in the project:

```python
import httpx
import orjson

def make_http_request():
    return httpx.get("https://example.com")

def dump_json():
    return orjson.dumps({"foo": "bar"})
```

_deptry_ will report `orjson` as a misplaced development dependency because it is used in non-development code.

To fix the issue, `orjson` should be moved from `[tool.pdm.dev-dependencies]` to `[project.dependencies]`:


```toml
[project]
dependencies = [
    "httpx==0.23.1",
    "orjson==3.8.3",
]

[tool.pdm.dev-dependencies]
test = ["pytest==7.2.0"]
```
