"""
Funcionalidades compartilhadas por todos modulos de teste
"""
from pprint import pformat
from base64 import b64encode
from hashlib import md5
from functools import singledispatch, wraps
import json
from types import SimpleNamespace
from random import choice, random, randint
import pytest
import lark
import os
from pathlib import Path

PATH = Path(__file__).parent


@pytest.fixture(scope="session")
def data():
    return data_fn


prob = lambda p: random() < p
digit = lambda ds="123456789": choice(ds)
randrange = lambda a, b: range(a, randint(a, b) + 1)
rint = lambda: (
    digit() + "".join("_" if prob(0.25) else digit() for _ in randrange(0, 10))
)


def check_int(ex: str):
    n = ex.replace("_", "")
    assert not ex.startswith("_")
    assert n
    assert n.isdigit()


def data_fn(name):
    if name.endswith('.py'):
        with open(PATH / "data" / name, encoding="utf8") as fd:
            return fd.read()
    
    with open(PATH / "data" / (name + ".json"), encoding="utf8") as fd:
        return json.load(fd)
