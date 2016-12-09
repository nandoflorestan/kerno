"""Action base class."""

from abc import ABCMeta, abstractmethod
from sys import exc_info
from traceback import format_tb
from bag.web.exceptions import Problem


class Action(metaclass=ABCMeta):
    """Base for Action classes. Actions are composable and chainable."""

    def __init__(self, peto, **kw):
        self.peto = peto
        for key, val in kw.items():
            setattr(self, key, val)

    @abstractmethod
    def __call__(self):
        """Override this method to do the main work of the action.

        Instead of returning something, modify self.peto.rezulto.
        """

    # @abstractmethod  # prevents instantiation when not implemented
    # def undo(self):
        """Optionally also implement undo for this action."""
