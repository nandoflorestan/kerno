"""A better way to send entities through the wire.

What problems does this solve?

1. Python model classes do not need to implement ``as_dict()``. Instead, you
implement a variation of a ``jsonright()`` function in a separate step,
which could even be in a separate package, totally decoupled. This does
`single dispatch`_ -- please learn about this.

.. _`single dispatch`: https://docs.python.org/3/library/functools.html#functools.singledispatch

2. When we send objects through the wire, different detail levels are
commonly needed -- for instance, first we only want the names of users to be
shown in a list, and then in a separate step, we might want all the details
of a single user. Your ``jsonright()`` implementation receives a ``features``
argument which can be a set of strings (or a sequence of any type)
specifying the level of detail. This keeps the API uniform.

3. This module also offers tools to help you write those
``jsonright()`` implementations -- especially ``entity2dict()``.

4. Sending common JSON through the wire has a problem: the repetition of keys.
For example, if you output a list of users, the keys of each object, such as
"id", "name", "email" etc. are repeated for each instance in the JSON.
Here we save bandwidth by encoding the data differently and then
reassembling it in the client.

5. The ``jsonright()`` interface has a ``peto`` argument, therefore when
implementing it you have access to the context, including application
configuration, repository (data access layer), current user etc.

How are data organized to save bandwidth?
=========================================

jsonright avoids repeating key names when outputting sequences of entities
in JSON. It pivots the table so it grows to the right::

    [
        ["id", 1, 2],
        ["email", "ex@am.pl", "sagan@nasa.gov"],
    ]

Of course objects are easily reassembled in Javascript.  The function that
does that is in the file kerno.js.

Usage
=====

Please see a usage example in
`our tests <https://github.com/nandoflorestan/kerno/blob/master/tests/test_web_jsonright.py>`_.
"""

from datetime import date, datetime
from decimal import Decimal
from functools import singledispatch
from typing import Any, Iterable, Sequence

from bag import first
from kerno.peto import AbsUserlessPeto
from kerno.typing import DictStr


def keys_from(obj: Any) -> Iterable[str]:
    """Return the names of the instance variables of ``obj``."""
    return vars(obj).keys()


def only_relevant(keys: Iterable[str]) -> Iterable[str]:
    """Ignore strings that start in dunder ("__") or in "_sa_".

    These usually keep SQLAlchemy state.
    """
    return filter(
        lambda key: not key.startswith("__") and not key.startswith("_sa_"),
        keys,
    )


def excluding(blacklist: Sequence[str], keys: Iterable[str]) -> Iterable[str]:  # noqa
    return filter(lambda k: k not in blacklist, keys)


def entity2dict(
    obj: Any,
    keys: Iterable[str] = (),
) -> DictStr:
    """Dump certain instance variables of ``obj`` into a dictionary.

    This function is reusable.

    If you do not provide any ``keys``, a sensible default is used.
    """
    kk = keys or excluding(("password",), only_relevant(keys_from(obj)))
    return {key: getattr(obj, key) for key in kk}


@singledispatch
def jsonright(obj: Any, peto: AbsUserlessPeto, features=(), **kw) -> Any:
    """Overloadable function to encode entities for sending through the wire.

    You can register your own implementations which get called depending
    on the type of *obj*.
    """
    raise NotImplementedError(
        f"No implementation of jsonright() registered for type {type(obj)}"
    )


@jsonright.register(str)
@jsonright.register(int)
@jsonright.register(float)
@jsonright.register(bool)
@jsonright.register(type(None))
def _a(obj, peto: AbsUserlessPeto, features=(), **kw) -> Any:
    return obj


@jsonright.register(bytes)
def _b(obj, peto: AbsUserlessPeto, features=(), **kw) -> Any:
    return obj.decode(kw.get("encoding", "utf-8"))


@jsonright.register(Decimal)
def _c(obj, peto: AbsUserlessPeto, features=(), **kw) -> float:
    return float(str(obj))


@jsonright.register(datetime)
@jsonright.register(date)
def _d(obj, peto: AbsUserlessPeto, features=(), **kw) -> str:
    return obj.isoformat()


@jsonright.register(dict)
def _e(obj, peto: AbsUserlessPeto, features=(), **kw) -> DictStr:
    return {
        str(key): jsonright(val, peto, features, **kw) for (key, val) in obj.items()
    }


primitive_types = (
    str,
    bytes,
    int,
    float,
    bool,
    type(None),
    Decimal,
    date,
    datetime,
    dict,
)


@jsonright.register(list)
@jsonright.register(tuple)
@jsonright.register(set)
@jsonright.register(frozenset)
def _s(obj, peto: AbsUserlessPeto, features=(), **kw) -> Sequence:
    if len(obj) == 0:
        return []
    first_item = first(obj)
    if isinstance(first_item, primitive_types):
        return [jsonright(item, peto, features, **kw) for item in obj]
    # Below this line we assume we are dealing with a sequence of entities.
    # In this case we pivot data in order to save bandwidth.
    first_dict = jsonright(first_item, peto, features, **kw)
    ret = [[key] for key in first_dict]
    for entity in obj:
        adict = jsonright(entity, peto, features, **kw)
        for alist in ret:
            alist.append(jsonright(adict[alist[0]], peto, features, **kw))
    return ret
