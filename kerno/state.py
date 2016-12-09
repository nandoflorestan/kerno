"""Classes that store state."""

from copy import copy
from datetime import datetime


class UIMessage:
    """Represents a message to be displayed to the user in the UI."""

    KINDS = ['danger', 'warning', 'info', 'success']

    def __init__(self, title, kind='success', plain=None, html=None):
        """Constructor.

        ``kind`` must be one of ('danger', 'warning', 'info', 'success').
        """
        assert (plain and not html) or (html and not plain)
        if kind == 'error':
            kind = 'danger'
        assert kind in self.KINDS, 'Unknown kind of message: "{0}". ' \
            "Possible kinds are {1}".format(kind, self.KINDS)
        self.title = title
        self.plain = plain
        self.html = html

    def __repr__(self):
        return '<{} "{}">'.format(self.__class__.__name__, self.title)

    def to_dict(self):
        """Convert instance to a dictionary, usually for JSON output."""
        return copy(self.__dict__)


class Peto:
    """State bag for an operation in progress.

    It's the same as a *request* in a web framework. In Kerno, each
    action in an operation may modify the *peto*. This is how an action
    sends data to the next action.
    """

    def __init__(self, kerno, user, operation, payload: dict, when=None, **kw):
        """Constructor.

        ``kerno`` must be the Kerno instance for the current application.
        ``user`` is the User instance requesting the current operation.
        ``operation`` is the activity being requested by the user.
        ``payload`` is a dictionary containing the operation parameters.
        """
        self.kerno = kerno
        self.when = when or datetime.utcnow()
        self.user = user      # the user or component requesting this action
        self.operation = operation
        self.dirty = payload  # dictionary containing the action parameters
        self.clean = None     # validation converts ``dirty`` to ``clean``
        self.rezulto = Rezulto()
        for key, val in kw.items():
            setattr(self, key, val)


class Returnable:
    """Base class for Rezulto and for MalbonaRezulto.

    Subclasses must define a ``status_int`` variable.
    """

    def __init__(self):
        """Base constructor."""
        self.messages = []  # Grave messages for the user to read
        self.toasts = []    # Quick messages that disappear automatically
        self.debug = {}     # Not displayed to the user
        self.redirect = None  # URL to redirect to

    def __repr__(self):
        return "<{} status: {}>".format(
            self.__class__.__name__, self.status_int)

    def to_dict(self):
        """Convert instance to a dictionary, usually for JSON output."""
        return copy(self.__dict__)

    def add_message(self, title, plain=None, html=None):
        """Add to the grave messages to be displayed to the user on the UI."""
        self.messages.append(UIMessage(title, plain=plain, html=html))

    def add_toast(self, title, plain=None, html=None):
        """Add to the quick messages to be displayed to the user on the UI."""
        self.toasts.append(UIMessage(title, plain=plain, html=html))


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

    def __init__(self, status_int=400):
        """Constructor."""
        Returnable.__init__(self)
        self.status_int = status_int
