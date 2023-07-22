"""Variables I commonly use when writing Python typing annotations."""

from typing import Any, NewType, TypeVar

# For generic functions. Represents a model instance of any type.
Entity = TypeVar("Entity")

# These are very common dict type annotations, I think an alias can be useful
DictStr = dict[str, Any]
DictInt = dict[int, Any]

# Add a semantic layer to strings and integers
TEmailAddress = NewType("TEmailAddress", str)
TPersonsName = NewType("TPersonsName", str)
