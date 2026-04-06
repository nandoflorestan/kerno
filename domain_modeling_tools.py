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

from typing import Protocol, NewType, Annotated, Literal, TypeAlias, get_args
from dataclasses import dataclass

# Tiny types: Prevent primitive obsession by wrapping base types.
UserId = NewType("UserId", int)
user_id = UserId(42)

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
# You can get the values at runtime, so it's like a better Enum:
order_states: tuple[str, ...] = get_args(OrderState)


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


# Invariant, covariant and contravariant generics
# ===============================================

from typing import TypeVar, Generic


class Animal: ...


class Cat(Animal): ...


# Invariant: Must be exactly the type (e.g., a List)
# Use when the container is both read from AND written to.
I = TypeVar("I")


class Box(Generic[I]):
    def set(self, item: I): ...
    def get(self) -> I: ...


# Covariant: Can be the type or a subtype (e.g., a Tuple)
# Use for "Producers" (read-only).
Co = TypeVar("Co", covariant=True)


class ImmutableList(Generic[Co]):
    def get(self) -> Co: ...


# Contravariant: Can be the type or a supertype
# Use for "Consumers" (write-only).
Contra = TypeVar("Contra", contravariant=True)


class Sink(Generic[Contra]):
    def send(self, item: Contra): ...


# Usage logic:
# Box[Cat] cannot be Box[Animal]
# ImmutableList[Cat] is a subtype of ImmutableList[Animal]
# Sink[Animal] is a subtype of Sink[Cat]
