"""DO NOT use this module.

It is a work in progress that currently brings no benefit to your app.
"""

from types import FunctionType
from kerno.action import Action
from kerno.kerno import Kerno
from kerno.state import Rezulto

from typing import TYPE_CHECKING, Any, Callable, Union, Type, cast

if TYPE_CHECKING:
    from typing import Dict  # noqa

TypActionFunction = Callable[..., Rezulto]  # a function that returns a Rezulto
TypActionClass = Type[Action]  # a subclass of Action
TypAction = Union[TypActionClass, TypActionFunction]  # either of these


class ActionRegistry:
    """A registry for all the business operations of an application."""

    def __init__(self, kerno: Kerno):
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
                "An action with the name {} is already registered.".format(
                    name
                )
            )
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
            action_instance = cast(
                TypActionFunction,
                action(kerno=self.kerno, user=user, repo=repo),
            )
            return action_instance(**kw)
        elif isinstance(action, FunctionType):
            return action(kerno=self.kerno, user=user, repo=repo, **kw)
        else:
            raise TypeError(
                '"{}" is not a function or an Action subclass!'.format(action)
            )
