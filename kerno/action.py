"""An abstract base for class-based actions."""

from abc import ABCMeta
from typing import Any

from kerno.kerno import Kerno


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

    def __init__(self, kerno: Kerno, user: Any, repo: Any) -> None:  # noqa
        self.kerno = kerno
        self.user = user
        self.repo = repo
