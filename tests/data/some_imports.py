from os import chdir, walk
from pathlib import Path
from typing import List

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

try:
    import click
except:
    import not_click


def func():
    import module_in_func


class MyClass:
    def __init__(self):
        import module_in_class
