#!/usr/bin/env python3
# Script originally from isort: https://github.com/PyCQA/isort/blob/4ccbd1eddf564d2c9e79c59d59c1fc06a7e35f94/scripts/mkstdlibs.py

from sphinx.ext.intersphinx import fetch_inventory

URL = "https://docs.python.org/{}/objects.inv"
PATH = "deptry/stdlibs/py{}.py"
VERSIONS = [("3", "7"), ("3", "8"), ("3", "9"), ("3", "10")]

DOCSTRING = """
File contains the standard library of Python {}.

DO NOT EDIT. If the standard library changes, a new list should be created
using the mkstdlibs.py script.
"""


class FakeConfig:
    intersphinx_timeout = None
    tls_verify = True
    user_agent = ""


class FakeApp:
    srcdir = ""
    config = FakeConfig()


for version_info in VERSIONS:
    version = ".".join(version_info)
    url = URL.format(version)
    invdata = fetch_inventory(FakeApp(), "", url)

    # Any modules we want to enforce across Python versions stdlib can be included in set init
    modules = {"_ast", "posixpath", "ntpath", "sre_constants", "sre_parse", "sre_compile", "sre"}
    for module in invdata["py:module"]:
        root, *_ = module.split(".")
        if root not in ["__main__"]:
            modules.add(root)

    path = PATH.format("".join(version_info))
    with open(path, "w") as stdlib_file:
        docstring = DOCSTRING.format(version)
        stdlib_file.write(f'"""{docstring}"""\n\n')
        stdlib_file.write("stdlib = {\n")
        for module in sorted(modules):
            stdlib_file.write(f'    "{module}",\n')
        stdlib_file.write("}\n")
