"""Action base class."""

from abc import ABCMeta, abstractmethod


class Action(metaclass=ABCMeta):
    """Base for Action classes. Actions are composable and chainable.

    If you don't need undo functionality, you may skip subclassing Action and
    just write a function that takes the argument ``peto``.
    Instead of returning something, it should modify ``peto.rezulto``.
    """

    def __init__(self, peto):  # , **kw):
        """Constructor."""
        self.peto = peto
        # for key, val in kw.items():
        #     setattr(self, key, val)

    @abstractmethod
    def __call__(self):
        """Override this method to do the main work of the action.

        Instead of returning something, modify self.peto.rezulto.
        """
        pass

    # @abstractmethod  # prevents instantiation when not implemented
    # def undo(self):
        """Optionally also implement undo for this action."""
