"""A base class for SQLAlchemy-based repositories."""

from typing import Any, Generic, Iterable, List, Optional, Sequence, Tuple

from kerno.kerno import Kerno
from kerno.typing import DictStr, Entity


class SpyRepo:
    """Nice test double, can be inspected at the end of a test."""

    def __init__(self, **kw) -> None:  # noqa
        self.new: List[Any] = []
        self.deleted: List[Any] = []
        self.flushed = False
        for key, val in kw.items():
            setattr(self, key, val)

    def add(self, entity: Entity) -> Entity:  # noqa
        self.new.append(entity)
        return entity

    def add_all(self, entities: Sequence[Entity]) -> None:  # noqa
        self.new.extend(entities)

    def delete(self, entity) -> None:  # noqa
        self.deleted.append(entity)

    def flush(self) -> None:  # noqa
        self.flushed = True


class BaseSQLAlchemyRepository:
    """Base class for a SQLAlchemy-based repository."""

    SAS = "session factory"  # name of the SQLAlchemy session utility

    def __init__(self, kerno: Kerno, session_factory: Any = None):
        """Construct a SQLAlchemy repository instance to serve ONE request.

        - ``kerno`` is the Kerno instance for the current application.
        - ``session_factory`` is a function that returns a
          SQLAlchemy session to be used in this request -- scoped or not.
          If not provided as an argument, get it from the
          kerno utility registry (under the "session factory" name.
        """
        self.kerno = kerno
        self.sas = self.new_sas(session_factory or kerno.utilities[self.SAS])
        assert self.sas

    def new_sas(self, session_factory):
        """Obtain a new SQLAlchemy session instance."""
        assert session_factory is not None
        is_scoped_session = hasattr(session_factory, "query")
        # Because we don't want to depend on SQLAlchemy:
        if callable(session_factory) and not is_scoped_session:
            return session_factory()
        else:
            return session_factory

    def add(self, entity: Entity) -> Entity:
        """Add an object to the SQLAlchemy session, then return it."""
        self.sas.add(entity)
        return entity

    def add_all(self, entities: Sequence[Entity]) -> None:
        """Add model instances to the SQLAlchemy session."""
        self.sas.add_all(entities)

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
        assert not hasattr(entity, "_is_new")
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
        assert "_is_new" not in props
        entity = self._get_or_add(cls, **filters)
        for key, val in props.items():
            setattr(entity, key, val)
        return entity

    def update_association(
        self,
        cls: type,
        field: str,
        ids: Sequence[int],
        filters: DictStr,
        synchronize_session=None,
    ) -> List[Entity]:
        """Update a many-to-many relationship.  Return only NEW associations."""
        return update_association(
            cls=cls,
            field=field,
            ids=ids,
            filters=filters,
            sas=self.sas,
            synchronize_session=synchronize_session,
        )

    def get_or_create(self, cls: type, **filters) -> Tuple[Any, bool]:
        """Retrieve or add object; return a tuple ``(object, is_new)``.

        ``is_new`` is False if the object already existed in the database.
        """
        instance = self.sas.query(cls).filter_by(**filters).first()
        is_new = not instance
        if is_new:
            instance = cls(**filters)
            self.sas.add(instance)
        return instance, is_new

    def create_or_update(
        self, cls: type, values: DictStr = {}, **filters
    ) -> Tuple[Any, bool]:
        """Load and update entity if it exists, else create one.

        First obtain either an existing object or a new one, based on ``filters``.
        Then apply ``values`` and return a tuple ``(object, is_new)``.
        """
        instance, is_new = self.get_or_create(cls, **filters)
        for k, v in values.items():
            setattr(instance, k, v)
        return instance, is_new


def update_association(
    cls: type,
    field: str,
    ids: Sequence[int],
    filters: DictStr,
    sas,
    synchronize_session=None,
) -> List[Entity]:
    """Update a many-to-many relationship.  Return only NEW associations.

    When you have a many-to-many relationship, there is an association
    table between 2 main tables. The problem of setting the data in
    this case is a recurring one and it is solved here.
    Existing associations might be deleted and some might be created.

    Example usage::

        user = session.query(User).get(1)
        # Suppose there's a many-to-many relationship to Address,
        # through an entity in the middle named UserAddress which contains
        # just the columns user_id and address_id.
        new_associations = update_association(
            cls=UserAddress,      # the association class
            field='address_id'     # name of the remote foreign key
            ids=[5, 42, 89],        # the IDs of the user's addresses
            filters={"user": user},  # to load existing associations
            sas=my_sqlalchemy_session,
        )
        for item in new_associations:
            print(item)

    This method returns a list of any new association instances
    because you might want to finish the job by doing something
    more with them (e. g. setting other attributes).

    A new query is needed to retrieve the totality of the associations.
    """
    # Fetch eventually existing association IDs
    existing_ids = frozenset(
        [o[0] for o in sas.query(getattr(cls, field)).filter_by(**filters)]
    )

    # Delete association rows that we no longer want
    desired_ids = frozenset(ids)
    to_remove = existing_ids - desired_ids
    if to_remove:
        q_remove = (
            sas.query(cls)
            .filter_by(**filters)
            .filter(getattr(cls, field).in_(to_remove))
        )
        if synchronize_session is not None:
            q_remove.delete(synchronize_session=synchronize_session)
        else:
            for entity in q_remove:
                sas.delete(entity)

    # Create desired associations that do not yet exist
    to_create = desired_ids - existing_ids
    new_associations = []
    for id in to_create:
        association = cls(**filters)
        setattr(association, field, id)
        new_associations.append(association)
    sas.add_all(new_associations)
    return new_associations


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

    def all(self) -> List[Entity]:  # noqa
        ...

    def count(self) -> int:  # noqa
        ...

    def delete(self) -> None:  # noqa
        ...

    # def exists(self): ...  # noqa
    def first(self) -> Optional[Entity]:  # noqa
        ...

    def get(self, ident) -> Optional[Entity]:  # noqa
        ...

    def one(self) -> Entity:  # noqa
        ...

    # def slice(self, start: int, stop: Optional[int]): ...  # noqa
    def yield_per(self, count: int) -> List[Entity]:  # noqa
        ...
