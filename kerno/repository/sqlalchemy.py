"""A base class for SQLAlchemy-based repositories."""

from typing import Any, Generic, Iterable, List, Optional, TypeVar
from kerno.kerno import Kerno

Entity = TypeVar('Entity')  # For generic functions. Can be any type.


class BaseSQLAlchemyRepository:
    """Base class for a SQLAlchemy-based repository."""

    def __init__(self, kerno: Kerno, session_factory: Any) -> None:
        """Construct a SQLAlchemy repository instance to serve ONE request.

        - ``kerno`` is the Kerno instance for the current application.
        - ``session_factory`` is a function that returns a
          SQLAlchemy session to be used in this request -- scoped or not.
        """
        self.kerno = kerno
        self.sas = self.new_sas(session_factory)

    def new_sas(self, session_factory):
        """Obtain a new SQLAlchemy session instance."""
        is_scoped_session = hasattr(session_factory, 'query')
        # Because we don't want to depend on SQLAlchemy:
        if callable(session_factory) and not is_scoped_session:
            return session_factory()
        else:
            return session_factory

    def add(self, entity: Entity) -> Entity:
        """Add an object to the SQLAlchemy session, then return it."""
        self.sas.add(entity)
        return entity

    def delete(self, entity: Entity) -> None:
        """Delete an ``entity`` from the database."""
        self.sas.delete(entity)

    def flush(self) -> None:
        """Obtain IDs on new objects and update state on the database.

        Without committing the transaction.
        """
        self.sas.flush()


class Query(Iterable, Generic[Entity]):
    """Typing stub for a returned SQLAlchemy query.

    This is purposely very incomplete.  It is intended to be used as return
    value in repository methods, such that user code can use, but not change,
    the returned query, which is what we like to do in this architecture.

    If you want a more complete implementation, try
    https://github.com/dropbox/sqlalchemy-stubs

    Their query stub is at
    https://github.com/dropbox/sqlalchemy-stubs/blob/master/sqlalchemy-stubs/orm/query.pyi
    """

    def all(self) -> List[Entity]: ...
    def count(self) -> int: ...
    # def exists(self): ...
    def first(self) -> Optional[Entity]: ...
    def get(self, ident) -> Optional[Entity]: ...
    def one(self) -> Entity: ...
    # def slice(self, start: int, stop: Optional[int]): ...
    def yield_per(self, count: int) -> List[Entity]: ...
