import typing
from os import chdir, walk
from pathlib import Path
from typing import List, TYPE_CHECKING
from importlib import import_module
from importlib import import_module as im
import importlib
import importlib as il

import numpy as np
import pandas
from numpy.random import sample

from . import foo
from .foo import bar

x = 1
if x > 0:
    import httpx
elif x < 0:
    from baz import Bar
else:
    import foobar

import barfoo as bf
from randomizer import random

if TYPE_CHECKING:
    import mypy_boto3_s3

if typing.TYPE_CHECKING:
    import mypy_boto3_sagemaker

try:
    import click
except:
    import not_click


def func():
    import module_in_func


class MyClass:
    def __init__(self):
        import module_in_class

import_module("patito")
importlib.import_module("polars")
im("uvicorn")
import_module("http.server")
il.import_module("xml.etree.ElementTree")
