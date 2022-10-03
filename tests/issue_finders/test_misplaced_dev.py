from deptry.issue_finders.misplaced_dev import MisplacedDevDependenciesFinder
from deptry.module import Module


def test_simple():
    dependencies = ["bar"]
    dev_dependencies=["foo"]
    modules = [Module("foo", dev_top_levels=["foo"], is_dev_dependency=True)]
    deps = MisplacedDevDependenciesFinder(imported_modules=modules, dependencies=dependencies, dev_dependencies=dev_dependencies).find()
    assert len(deps) == 1
    assert deps[0] == "foo"
