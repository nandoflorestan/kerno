"""Variables I commonly use when writing Python typing annotations."""

from typing import Any, Dict, TypeVar

# For generic functions. Represents a model instance of any type.
Entity = TypeVar("Entity")

# These are very common Dict type annotations, I think an alias can be useful
DictStr = Dict[str, Any]
DictInt = Dict[int, Any]
