
# FAQ

### What kind of issues does _deptry_ detect?

_deptry_ looks for four kinds of issues:

- Obsolete dependencies: Dependencies which are added to your project's dependencies, but which are not used within the codebase.
- Missing dependencies: Modules that are imported within your project, but no corresponding package is found in the environment or the dependencies.
- Transitive dependencies: Packages from which code is imported, but the package itself is not in your projects dependencies. For example, assume your project has a `.py` file that imports module A. However, A is not in your project's dependencies. Instead, another package (B) is in your list of dependencies, which in turn depends on A. Package A should be explicitly added to your project's list of dependencies.
- Misplaced dependencies: Development dependencies that should be included as regular dependencies.
