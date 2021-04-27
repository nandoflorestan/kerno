"""An abstract base for class-based actions."""

from abc import ABCMeta

from kerno.peto import AbstractPeto


class Action(metaclass=ABCMeta):
    """Abstract base for class-based actions.

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
