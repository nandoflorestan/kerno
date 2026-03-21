"""Interfaces for a well-architected application.

See example implementations in bases.py.
"""

from types import MappingProxyType  # which behaves like a FrozenDict
from typing import Any, Callable, Generic, Sequence, Tuple, Type, TypeVar, Protocol

from kerno.typing import DictStr, Entity


class IConfig(Protocol):
    """Interface for an application's validated configuration object."""

    kerno_utilities: DictStr  # A map of names to importables


class IKerno(Protocol):
    """Interface for the core of an application, integrating decoupled resources.

    The Kerno instance should be a singleton; its lifetime is the longest.

    The Kerno instance is used at runtime; at startup it is built by
    the "Eko" configurator.
    """

    config: IConfig
    const: DictStr  # The app should put global constants here
    utilities: MappingProxyType[str, Any]  # a frozen map of name to utility
    # Suggestion: If your app needs events, add to your Kerno our EventHub:
    # events: EventHub  # from kerno.event import EventHub


TKerno = TypeVar("TKerno", bound=IKerno)


class IRepo(Protocol):
    """Base interface for a repository (many more methods expected)."""

    def add(self, entity: Entity) -> Entity: ...

    def add_all(self, entities: Sequence[Entity]) -> None: ...

    def delete(self, entity: Entity) -> None: ...

    def flush(self) -> None: ...

    def get_or_create(
        self, cls: Type[Entity], **filters: Any
    ) -> Tuple[Entity, bool]: ...

    def create_or_update(
        self, cls: Type[Entity], values: DictStr = {}, **filters: Any
    ) -> Tuple[Entity, bool]: ...

    def update_association(
        self,
        cls: Type[Entity],
        field: str,
        ids: Sequence[int],
        filters: DictStr,
        synchronize_session: Any = None,
    ) -> list[Entity]: ...


class IUserlessPeto(Protocol):
    """Context for actions NOT done by a logged user."""

    kerno: IKerno  # the global application object
    repo: IRepo  # the data access layer
    raw: DictStr  # operation-specific data (request parameters)


class IEmailUser(Protocol):

    id: int
    email: str
    # short_name: str
    # full_name: str


class IPeto(IUserlessPeto, Protocol):
    """Context for actions done by a logged user. Extends TUserlessPeto."""

    user: IEmailUser  # the current user requesting an operation. Not None!
