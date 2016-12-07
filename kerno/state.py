"""Classes that store state."""

from copy import copy
from sys import exc_info
from traceback import format_tb
from bag.web.exceptions import Problem


class Peto:
    """State bag for an operation in progress.

    It's the same as a *request* in a web framework. In Kerno, each
    action in an operation may modify the *peto*. This is how an action
    sends data to the next action.
    """

    def __init__(self, kerno, user, operation, payload: dict, **kw):
        """Constructor.

        ``kerno`` must be the Kerno instance for the current application.
        ``user`` is the User instance requesting the current operation.
        ``operation`` is the activity being requested by the user.
        ``payload`` is a dictionary containing the operation parameters.
        """
        self.kerno = kerno
        self.user = user      # the user or component requesting this action
        self.operation = operation
        self.dirty = payload  # dictionary containing the action parameters
        self.clean = None     # validation converts ``dirty`` to ``clean``
        self.rezulto = Rezulto()
        for key, val in kw.items():
            setattr(self, key, val)


class Returnable:
    """Base class for Rezulto and for MalbonaRezulto."""

    def __init__(self):
        """Base constructor."""
        self.messages = []  # Grave messages for the user to read
        self.toasts = []    # Quick messages that disappear automatically
        self.debug = {}     # Not displayed to the user
        self.redirect = None  # URL to redirect to

    def to_dict(self):
        """Convert instance to a dictionary, usually for JSON output."""
        return copy(self.__dict__)


class Rezulto(Returnable):
    """Response object returned from a successful operation.

    Unsuccessful operations raise exceptions instead.
    """

    def __init__(self):
        """Constructor."""
        super().__init__()
        self.payload = {}

    @property
    def status_int(self):
        """Hopefully the appropriate HTTP response code indicating success.

        200 if we are returning data; 201 if there is no payload.
        """
        return 200 if self.payload else 201

    def to_dict(self):
        """Convert instance to a dictionary, usually for JSON output."""
        adict = super().to_dict()
        adict['status_int'] = self.status_int
        return adict


class MalbonaRezulto(Returnable, Exception):
    """Base class for exceptions raised by Kerno."""

    def __init__(self, errors=None, status_int=400):
        """Constructor."""
        Returnable.__init__(self)
        self.status_int = status_int
        self.errors = errors or {}  # For validation errors
