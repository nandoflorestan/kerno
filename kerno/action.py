"""Helpers for business layers of applications.

Also a DEPRECATED abstract base for class-based actions.
"""

from typing import Any, Generic, Iterable
from warnings import warn

from abc import ABCMeta

from kerno.peto import AbstractPeto
from kerno.typing import Entity


class Action(metaclass=ABCMeta):
    """DEPRECATED abstract base for class-based actions.

    Subclasses must implement __call__() and, if happy,
    return a Rezulto instance::

        from kerno.action import Action
        from kerno.state import Rezulto

        class MyAction(Action):
            def __call__(self, *a, **kw) -> Rezulto:
                ...
    """

    def __init__(self, peto: AbstractPeto):  # noqa
        warn("kerno.Action is deprecated and will be removed.", DeprecationWarning)
        self.peto = peto

    @property
    def kerno(self):
        """Return the global application object."""
        return self.peto.kerno

    @property
    def repo(self):
        """Return a repository instance for the current request."""
        return self.peto.repo

    @property
    def user(self):
        """Return the current user or None."""
        return self.peto.user


class EntityComparison(Generic[Entity]):
    """Find the differences between two entities."""

    def __init__(self, old: Entity, new: Entity):  ## noqa
        self.old = old
        self.new = new

    def get_differences(
        self, var_names: Iterable[str] = ()
    ) -> list[tuple[str, Any, Any]]:
        """Find the differences between the two entities.

        Pay attention only to the relevant *var_names*.
        """
        if not var_names:
            var_names = list(self.old.__dict__.keys())
            if "password" in var_names:
                var_names.remove("password")
        ret = []
        for name in var_names:
            old_value = getattr(self.old, name)
            new_value = getattr(self.new, name)
            if old_value != new_value:
                ret.append((name, old_value, new_value))
        return ret

    @staticmethod
    def to_str(differences: Iterable[tuple[str, Any, Any]], sep=" ") -> str:
        """Return text stating the differences. The separator is configurable."""
        diffs = [f"{d[0]} changed from «{d[1]}» to «{d[2]}»." for d in differences]
        return sep.join(diffs)

    def __str__(self) -> str:  # noqa
        return self.to_str(self.get_differences())


class OrganizeHashableObjects(Generic[Entity]):
    """Given current and desired collections, sort objects into to_add and to_remove.

    This implementation uses sets. In Python, sets and dictionaries gain
    their speed by using hashing as a fast approximation of
    full equality checking. Therefore, the objects must
    implement __hash__, or be tuples.
    """

    def __init__(
        self, existing_objects: Iterable[Entity], desired_objects: Iterable[Entity]
    ):
        """Organize through sets."""
        set_desired: set[Entity] = set(desired_objects)
        set_existing: set[Entity] = set(existing_objects)
        self.to_keep: set[Entity] = set_desired.intersection(set_existing)

        set_desired.difference_update(self.to_keep)
        self.to_add: set[Entity] = set_desired

        set_existing.difference_update(self.to_keep)
        self.to_remove: set[Entity] = set_existing


class OrganizeValueObjects(Generic[Entity]):
    """Given current and desired collections, sort objects into to_add and to_remove.

    This version loops testing equality, so the objects must
    implement __eq__, or be dictionaries or tuples. Providing your own
    equality function is also possible via the argument *eq_fn*.

    In the output, *to_keep* contains instances of EntityComparison,
    so it is then possible to find further differences between the
    existing and desired objects, by considering more variables.

    This helps figure out what objects to delete from a DB, what
    objects to add, and what objects to alter, with minimal interference
    in the database. The alternatives are either to crudely
    delete then add everything, or to write lots of ad hoc code.
    """

    def __init__(
        self,
        existing_objects: Iterable[Entity],
        desired_objects: Iterable[Entity],
        eq_fn=None,
    ):
        """Organize through iteration and comparison."""
        self.to_add: list[Entity] = []
        self.to_remove: list[Entity] = []
        self.to_keep: list[EntityComparison] = []
        self.updated: list[Entity] = []
        for wanted in desired_objects:
            found = False
            for given in existing_objects:
                if eq_fn(wanted, given) if eq_fn else (wanted == given):
                    self.to_keep.append(EntityComparison(old=given, new=wanted))
                    found = True
                    break
            if found:
                continue
            # Desired but not existing, therefore we need to add it.
            self.to_add.append(wanted)
        for given in existing_objects:
            found = False
            for wanted in desired_objects:
                if eq_fn(wanted, given) if eq_fn else (wanted == given):
                    found = True
                    break
            if found:
                continue
            # Existing but not desired, therefore we need to remove it.
            self.to_remove.append(given)

    def update_kept_entities(self, var_names: Iterable[str] = ()) -> list[Entity]:
        """If kept entities have desired differences, apply these changes.

        The changed objects are found in .updated.
        """
        for comparison in self.to_keep:
            tups = comparison.get_differences(var_names=var_names)
            for var_name, old_value, new_value in tups:
                setattr(comparison.old, var_name, new_value)
                self.updated.append(comparison.old)
        return self.updated

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} add:{len(self.to_add)} "
            f"keep:{len(self.to_keep)} del:{len(self.to_remove)}>"
        )
