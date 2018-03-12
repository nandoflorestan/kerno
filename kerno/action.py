"""A registry for all the business operations of an application."""

from abc import ABCMeta, abstractmethod
from types import FunctionType
from .core import Kerno
from .state import Rezulto

from typing import TYPE_CHECKING, Any, Callable, Union, Type, cast
if TYPE_CHECKING:
    from typing import Dict  # noqa


class Action(metaclass=ABCMeta):
    """Abstract base for class-based actions."""

    def __init__(self, kerno: Kerno, user: Any, repo: Any) -> None:
        """Construct."""
        self.kerno = kerno
        self.user = user
        self.repo = repo

    @abstractmethod
    def __call__(self, **kw) -> Rezulto:
        """Must be overridden in subclasses and return a Rezulto."""


TypActionFunction = Callable[..., Rezulto]  # a function that returns a Rezulto
TypActionClass = Type[Action]               # a subclass of Action
TypAction = Union[TypActionClass, TypActionFunction]  # either of these


class ActionRegistry:
    """Kerno's action registry."""

    def __init__(self, kerno: Kerno) -> None:
        """Construct.

        ``kerno`` must be the Kerno instance for the current application.
        """
        self.kerno = kerno
        self.actions = {}  # type: Dict[str, TypAction]

    def add(self, name: str, action: TypAction) -> None:
        """Register an Action under ``name`` at startup for later use."""
        # assert callable(action)
        if name in self.actions:
            raise ValueError(
                'An action with the name {} is already registered.'.format(
                    name))
        self.actions[name] = action

    def remove(self, name: str) -> None:
        """Delete the action with ``name``."""
        del self.actions[name]

    def run(self, name: str, user: Any, repo: Any, **kw) -> Rezulto:
        """Execute, as ``user``, the action stored under ``name``.

        ``user`` is the User instance requesting the current operation.

        This method will become more complex when we introduce events.
        """
        # when = when or datetime.utcnow()
        action = self.actions[name]
        if issubclass(cast(TypActionClass, action), Action):
            action_instance = cast(Action, action(
                kerno=self.kerno, user=user, repo=repo))
            return action_instance(**kw)
        elif isinstance(action, FunctionType):
            return action(kerno=self.kerno, user=user, repo=repo, **kw)
        else:
            raise TypeError(
                '"{}" is not a function or an Action subclass!'.format(action))
