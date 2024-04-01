"""Helpers for business layers of applications.

Also a DEPRECATED abstract base for class-based actions.
"""

from typing import Generic, Iterable

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

    This version loops testing equality, so the objects
    must implement __eq__, or be dictionaries or tuples.
    """

    def __init__(
        self,
        existing_objects: Iterable[Entity],
        desired_objects: Iterable[Entity],
        eq_fn=None,
    ):
        """Organize through iteration and comparison."""
        self.to_add: list[Entity] = []
        self.to_keep: list[Entity] = []
        self.to_remove: list[Entity] = []
        for d in desired_objects:
            found = False
            for e in existing_objects:
                if eq_fn(d, e) if eq_fn else (d == e):
                    self.to_keep.append(e)
                    found = True
                    break
            if found:
                continue
            # Desired but not existing, therefore we need to add it.
            self.to_add.append(d)
        for e in existing_objects:
            found = False
            for d in desired_objects:
                if eq_fn(d, e) if eq_fn else (d == e):
                    found = True
                    break
            if found:
                continue
            # Existing but not desired, therefore we need to remove it.
            self.to_remove.append(e)
