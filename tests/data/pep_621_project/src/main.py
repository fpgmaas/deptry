from os import chdir, walk
from pathlib import Path

import importlib_metadata
import click
import white as w
from urllib3 import contrib
import asyncio
import bs4
