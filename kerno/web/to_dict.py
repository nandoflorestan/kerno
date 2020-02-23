"""A setup so you can have many, powerful to_dict() implementations.

Our main objective is to **remove any JSON concerns from model classes**.
These should NOT contain ``as_dict()`` implementations because the system
may need multiple converters for the same model -- for instance,
with varying fields, verbosities, levels of detail,
optional inclusion of related entities etc.

**It is bad if AVerySpecificModel.as_dict() needs a different signature**
to accept a parameter that all the other as_dict() methods do not need.

Here is the solution:

By using `Reg <http://reg.readthedocs.io/en/latest/>`_ we now have a
``to_dict(obj, flavor='', **kw)`` function that dispatches
on the type of ``obj`` and ``flavor``. This allows you to register
more than one implementation (with a "flavor" name) for each of your
model classes.

In order to understand this, you need to know what Reg does:
multiple dispatch.

Our to_dict() function also has a default implementation, so it can be used
directly.

This way you can create a situation in which::

    to_dict(Address, flavor="")  # calls one implementation, and
    to_dict(Person, flavor="")  # calls another implementation, and
    to_dict(Person, flavor="table")   # calls yet another implementation.

If the user code omits the *flavor* argument, the default one -- whose
value is an empty string -- gets used.

And because our ``to_dict()`` accepts keyword arguments, you can create
a very powerful version of it, that can take such arguments as
a repository, a user object, the current date etc.

Please see a usage example in
`our tests <https://github.com/nandoflorestan/kerno/blob/master/tests/test_web_to_dict.py>`_.
"""

from collections import OrderedDict
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Iterable, Sequence
import reg


def keys_from(obj: Any) -> Iterable:
    """Return the names of the instance variables of ``obj``."""
    return obj.__dict__.keys()


def only_relevant(keys: Iterable[str]) -> Iterable[str]:
    """Ignore strings that start in dunder ("__") or in "_sa".

    These are usually keeping SQLAlchemy state.
    """
    return filter(
        lambda key: not key.startswith("__") and not key.startswith("_sa_"),
        keys,
    )


def excluding(blacklist: Sequence, keys: Iterable) -> Iterable:  # noqa
    return filter(lambda k: k not in blacklist, keys)


def reuse_dict(
    obj: Any,
    keys: Iterable = (),
    for_json: bool = True,
    sort: bool = True,
    **kw,
) -> OrderedDict:
    """Dump the instance variables of ``obj`` into an OrderedDict.

    This function is reusable and free of Reg dispatch.

    If the ``for_json`` flag is True, convert certain types.

    If the ``sort`` flag is True, sort the OrderedDict.
    """
    amap: OrderedDict[str, Any] = OrderedDict()
    kk = keys or excluding(("password",), only_relevant(keys_from(obj)))
    if sort:
        kk = sorted(kk)
    for key in kk:
        val = getattr(obj, key)
        # TODO Probably should treat Python types elsewhere!
        if for_json and (isinstance(val, datetime) or isinstance(val, date)):
            amap[key] = val.isoformat()
        elif for_json and isinstance(val, Decimal):
            amap[key] = float(str(val))
        elif for_json and not isinstance(
            val, (str, int, float, list, dict, bool, type(None))
        ):
            continue
        else:
            amap[key] = val
    return amap


@reg.dispatch(  # Dispatch on type of *obj* and value of *flavor*.
    reg.match_instance("obj"),
    reg.match_key("flavor", lambda obj, flavor, **kw: flavor),
)
# Cannot type-annotate this function, Reg 0.11 does not support it
def to_dict(obj, flavor="", **kw):
    """Overloadable version of our function ``reuse_dict``.

    You can register your own implementations depending on *obj* and *flavor*.
    """
    return reuse_dict(obj, **kw)


"""
Ideas
-----

- Use a JSON serializer without tree traversal, but support Python data types such as datetime
- convert datetime to {"_T": "Date", "val": "..."}... NO. Convert to string and the client must know that such and such attributes must be converted to Date. Maybe provide the mapping (or even JS code) as another string?
- provide SQLAlchemy converter based on mine -- No, because https://pypi.python.org/pypi/colander_jsonschema/
- Convert trees of objects
- optionally provide "_typ" in output... but better as a property of a collection?

Other JSON related projects
---------------------------

jsonplus has "exact" and "compat" serializers:
https://pypi.python.org/pypi/jsonplus/0.8.0

morejson converts to and from stdlib types:
https://pypi.python.org/pypi/morejson/1.1.5
https://pypi.python.org/pypi/jsontyping/1.0.3

https://github.com/atsuoishimoto/emitjson

https://pypi.python.org/pypi/hgijson/3.1.0

Annoying declarative API, but achieves a lot:
http://hgi-json.readthedocs.io/en/latest/functionality/

https://pypi.python.org/pypi/json_tricks/3.11.3


Outside my scope and purpose, but probably great
------------------------------------------------

jsonpickle does arbitrary trees (which we don't really want).
https://pypi.python.org/pypi/jsonpickle/

https://pypi.python.org/pypi/json-model/1.0.1
https://pypi.python.org/pypi/json-delta/2.0
https://pypi.python.org/pypi/json-merger/0.4.0
"""
