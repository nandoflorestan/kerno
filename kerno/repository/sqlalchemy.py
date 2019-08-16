"""A base class for SQLAlchemy-based repositories."""

from typing import Any, Generic, Iterable, List, Optional

from kerno.kerno import Kerno
from kerno.typing import DictStr, Entity


class BaseSQLAlchemyRepository:
    """Base class for a SQLAlchemy-based repository."""

    SAS = 'session factory'  # name of the SQLAlchemy session utility

    def __init__(self, kerno: Kerno, session_factory: Any = None):
        """Construct a SQLAlchemy repository instance to serve ONE request.

        - ``kerno`` is the Kerno instance for the current application.
        - ``session_factory`` is a function that returns a
          SQLAlchemy session to be used in this request -- scoped or not.
          If not provided as an argument, get it from the
          kerno utility registry (under the "session factory" name.
        """
        self.kerno = kerno
        self.sas = self.new_sas(
            session_factory or kerno.utilities[self.SAS])
        assert self.sas

    def new_sas(self, session_factory):
        """Obtain a new SQLAlchemy session instance."""
        assert session_factory is not None
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

    def _get_or_add(self, cls: type, **filters):
        """Retrieve or add an entity with ``filters``; return the entity.

        The entity will have a transient ``_is_new`` flag telling you whether
        it already existed.

        This is a helper for the implementation of repository methods and
        should not be used elsewhere.
        """
        entity = self.sas.query(cls).filter_by(**filters).first()
        if entity is None:
            entity = cls(**filters)
            self.add(entity=entity)
            is_new = True
        else:
            is_new = False
        assert not hasattr(entity, '_is_new')
        entity._is_new = is_new
        return entity

    def _update_or_add(self, cls: type, props: DictStr = {}, **filters):
        """Load and modify entity if it exists, else create one.

        First obtain either an existing object or a new one, based on
        ``filters``. Then apply ``props`` and return the entity.

        The entity will have a transient ``_is_new`` flag telling you whether
        it already existed.

        This is a helper for the implementation of repository methods and
        should not be used elsewhere.
        """
        assert '_is_new' not in props
        entity = self._get_or_add(cls, **filters)
        for key, val in props.items():
            setattr(entity, key, val)
        return entity


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

    def all(self) -> List[Entity]: ...  # noqa
    def count(self) -> int: ...  # noqa
    # def exists(self): ...  # noqa
    def first(self) -> Optional[Entity]: ...  # noqa
    def get(self, ident) -> Optional[Entity]: ...  # noqa
    def one(self) -> Entity: ...  # noqa
    # def slice(self, start: int, stop: Optional[int]): ...  # noqa
    def yield_per(self, count: int) -> List[Entity]: ...  # noqa
