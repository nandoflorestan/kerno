"""Variables I commonly use when writing Python typing annotations."""

from __future__ import annotations  # allows forward references; python 3.7+
from typing import Any, Dict, List, NewType, TypeVar, Union

# For generic functions. Represents a model instance of any type.
Entity = TypeVar("Entity")

# You should use a NewType for the id of each entity of yours; e. g.:
TUserId = NewType("TUserId", int)

# These are very common dict type annotations, I think an alias can be useful
DictInt = dict[int, Any]
DictStr = dict[str, Any]  # But a TypedDict is preferable when possible.

# Add a semantic layer to strings and integers
TEmailAddress = NewType("TEmailAddress", str)
TPersonsName = NewType("TPersonsName", str)
TURL = NewType("TURL", str)
# But these exist: from urllib.parse import urlsplit, SplitResult, urlparse, ParseResult
# https://docs.pydantic.dev/latest/api/networks/#pydantic.networks

Jsonable = Union[None, int, float, str, bool, List["Jsonable"], Dict[str, "Jsonable"]]
# If you expect a certain dictionary, again TypedDict is preferable.
# Tests
# a: Jsonable = {1: 1}  # Dict entry has incompatible type "int": "int"; expected "str"
