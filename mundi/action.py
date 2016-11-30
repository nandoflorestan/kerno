"""Action base class."""

from abc import ABCMeta, abstractmethod
from sys import exc_info
from traceback import format_tb
from bag.web.exceptions import Problem


class Action(metaclass=ABCMeta):
    """Base for Action classes. Actions are composable and chainable."""

    def __init__(self, mundi, agent, payload: dict, target_action=None, **kw):
        self.error = None  # and later, dict or False.
        self.status_int = None  # and later, an HTTP code.
        self.exception = None  # and later hopefully still None
        self.mundi = mundi
        self.agent = agent  # the user or component requesting this action
        # class of main requested action:
        self.target_action = target_action or type(self)
        self.payload = payload  # dictionary containing the action parameters

        for key, val in kw.items():
            setattr(self, key, val)

    @abstractmethod
    def do(self) -> dict:
        """Override this method to do the main work of the action.

        At the end return a dict with the payload for the next action.
        """

    # @abstractmethod  # prevents instantiation when not implemented
    # def undo(self):
        """Optionally also implement undo for this action."""

    def _succeed(self, status_int=200):
        self.error = False
        self.status_int = status_int

    def _fail(self, error_title, error_msg, error_debug=None, status_int=500,
              exception=None):
        self.error = {  # A dictionary ready for JSON output.
            "error_title": error_title,
            "error_msg": error_msg,
            "error_debug": error_debug,
        }
        self.status_int = int(status_int)
        self.exception = exception

    def steps(self):
        """The steps to execute this action. Override this rarely."""
        return self.do()

    def __call__(self):
        """Managed execution of this single action."""
        try:
            ret = self.steps()  # separate from exception handling below
        except Problem as e:
            self._fail(e.error_title, e.error_msg, e.error_debug,
                       status_int=e.status_int, exception=e)
            raise
        except Exception as e:
            typ, val, traceback = exc_info()
            traceback = format_tb(traceback)
            self._fail(error_title=str(typ), error_msg=str(e),
                       error_debug=traceback, exception=e)
            raise
        else:
            self._succeed()
            return ret
