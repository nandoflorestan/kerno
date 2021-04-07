"""Variables I commonly use when writing Python typing annotations."""

from typing import Any, Dict, NewType, TypeVar

# For generic functions. Represents a model instance of any type.
Entity = TypeVar("Entity")

# These are very common Dict type annotations, I think an alias can be useful
DictStr = Dict[str, Any]
DictInt = Dict[int, Any]

# Add a semantic layer to strings and integers
TEmailAddress = NewType("TEmailAddress", str)
TPersonsName = NewType("TPersonsName", str)
