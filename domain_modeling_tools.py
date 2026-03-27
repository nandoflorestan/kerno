"""This file is a cheatsheet for Scott Wlaschin's domain modeling style.

He always demonstrates in F# in his "Domain Modeling Made Functional" lectures,
so here are the static tools to do the same in Python.

Characteristics of this style:

- **Make illegal state unrepresentable.** (Through strict types.)
- Shameless type proliferation: well-defined types turn mypy into a huge ally.
    Often you don't need to write certain tests because mypy is being stricter.
- Avoid "primitive obsession" with more specific types.
    Purpose: documentation, and avoid a few bugs.
- Type composition (like lego), as opposed to subtyping (OO).
"""

from typing import Protocol, NewType, Annotated, Literal, TypeAlias
from dataclasses import dataclass

# Tiny types: Prevent primitive obsession by wrapping base types.
UserId = NewType("UserId", int)

# Constrained types: Using metadata for domain documentation.
Price = Annotated[float, "positive"]


# Records: Immutable data structures for domain entities.
@dataclass(frozen=True, kw_only=True)
class Customer:
    id: UserId
    name: str


# Optional values: Explicitly handling the absence of data.
EmailAddress: TypeAlias = str | None


# Union types: Modeling choices (Sum Types).
class Success: ...


class Failure: ...


Result: TypeAlias = Success | Failure

# Discrete states: Making illegal states unrepresentable via Literals.
OrderState = Literal["Pending", "Shipped", "Delivered"]


# Composition: Combining small types into complex domain models.
@dataclass(frozen=True)
class Order:
    state: OrderState
    total: Price


# Function signatures: Define a callable interface for dependency injection.
class Validator(Protocol):
    def __call__(self, value: str) -> bool: ...


# You can use the above function like this:
def process_data(data: str, check: Validator) -> None:
    if check(data):
        ...
