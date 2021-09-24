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


def leaves(tree):
    leaves = []

    def visit(node):
        for child in node.children:
            if isinstance(child, lark.Tree):
                visit(child)
            else:
                leaves.append(child)

    visit(tree)
    return leaves


def human_hash(x):
    h = special_hash(x)
    return b64encode(h).decode("ascii")


@singledispatch
def special_hash(x) -> bytes:
    raise NotImplementedError


@special_hash.register(int)
def _int(x):
    return b64encode(x.to_bytes(32, "").lstrip("\x00"))


@special_hash.register(str)
def _str(x):
    hasher = md5(x.encode("utf8"))
    return hasher.digest()


@special_hash.register(tuple)
@special_hash.register(list)
def _seq(xs):
    hasher = md5()
    for x in xs:
        hasher.update(special_hash(x))
    return f"{len(xs)}:".encode("ascii") + hasher.digest()


class Validators:
    METHODS = ["size"]

    def namespace(self):
        return SimpleNamespace(
            **{k: self.validator(getattr(self, k)) for k in self.METHODS}
        )

    def validator(self, fn):
        @wraps(fn)
        def func(*args):
            return lambda data: fn(data, *args)

        return func

    def size(self, data, size):
        if (n := len(data)) != size:
            raise AssertionError(
                f"tamanho incorreto: esperava {size}, mas obteve {n}\n"
                f"    valor inválido: {data}"
            )
