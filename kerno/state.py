"""Classes that store state."""

from abc import ABCMeta
from collections import OrderedDict
from typing import Any, Dict, List  # noqa
from kerno.web.to_dict import to_dict, reuse_dict


class UIMessage:
    """Represents a message to be displayed to the user in the UI."""

    KINDS = ["danger", "warning", "info", "success"]
    # The default to_dict() works fine for this class.

    def __init__(
        self, title: str="", kind: str="danger", plain: str="", html: str="",
    ) -> None:
        """Constructor.

        ``kind`` must be one of ("danger", "warning", "info", "success").
        """
        args_are_valid = (plain and not html) or (html and not plain)
        assert args_are_valid
        if kind == "error":
            kind = "danger"
        assert kind in self.KINDS, 'Unknown kind of message: "{0}". ' \
            "Possible kinds are {1}".format(kind, self.KINDS)
        self.kind = kind
        self.title = title
        self.plain = plain
        self.html = html

    def __repr__(self) -> str:
        return '<{} "{}">'.format(self.__class__.__name__, self.title)


class UICommand:
    """Represents a message telling the UI to do something."""

    __slots__ = ('name', 'payload')

    def __init__(self, name: str, payload: Dict[str, Any]) -> None:
        """Construct a message to the UI.

        ``name`` is the name of a command to be performed in the UI.
        ``payload`` is the data to run the command with.
        """
        self.name = name
        self.payload = payload

    def __repr__(self):
        return '<UICommand "{}">'.format(self.name)


@to_dict.register(obj=UICommand, flavor='')
def uicommand_to_dict(obj, flavor='', **kw):
    """Convert to dict a UICommand instance."""
    return OrderedDict((
        ('name', obj.name),
        ('payload', obj.payload)
    ))


class Returnable(metaclass=ABCMeta):
    """Base class for Rezulto and for MalbonaRezulto.

    Returnable is the base class for what Actions should return. It contains:

    - messages: Grave UI messages.
    - toasts: UI messages that disappear automatically after a while.
    - commands: messages to the UI, e. g., add an entity to your models
    - debug: A dict with information that is not displayed to the end user.
    - redirect: URL or screen to redirect to.

    Subclasses overload the ``status_int`` and ``kind`` static variables.
    """

    kind = "danger"
    status_int = 500  # HTTP response code indicating server bug/failure

    def __init__(
        self,
        commands: List[UICommand] = None,
        debug: Dict[str, Any] = None,
        redirect: str = '',
        **kw
    ) -> None:
        """Construct."""
        self.messages = []              # type: List[UIMessage]
        self.toasts = []                # type: List[UIMessage]
        self.commands = commands or []
        self.debug = debug or {}
        self.redirect = redirect
        for k, v in kw.items():
            setattr(self, k, v)

    def __repr__(self) -> str:
        return "<{} status: {}>".format(
            self.__class__.__name__, self.status_int)

    def add_message(
        self, title: str="", kind: str="", plain: str="", html: str="",
    ) -> UIMessage:
        """Add to the grave messages to be displayed to the user on the UI."""
        msg = UIMessage(
            title=title, kind=kind or self.kind, plain=plain, html=html)
        self.messages.append(msg)
        return msg

    def add_toast(
        self, title: str="", kind: str="", plain: str="", html: str="",
    ) -> UIMessage:
        """Add to the quick messages to be displayed to the user on the UI."""
        msg = UIMessage(
            title=title, kind=kind or self.kind, plain=plain, html=html)
        self.toasts.append(msg)
        return msg


@to_dict.register(obj=Returnable, flavor='')
def returnable_to_dict(obj, flavor='', **kw):
    """Convert instance to a dictionary, usually for JSON output."""
    amap = reuse_dict(
        obj=obj,
        keys=kw.get('keys', ('kind', 'status_int', 'debug', 'redirect')),
        sort=False)
    amap['messages'] = [reuse_dict(obj=msg) for msg in obj.messages]
    amap['toasts'] = [reuse_dict(obj=msg) for msg in obj.toasts]
    amap['commands'] = [to_dict(uicommand) for uicommand in obj.commands]
    return amap


class Rezulto(Returnable):
    """Well-organized successful response object.

    When your action succeeds you should return a Rezulto.
    Unsuccessful operations raise MalbonaRezulto instead.
    """

    kind = "success"
    status_int = 200  # HTTP response code indicating success


class MalbonaRezulto(Returnable, Exception):
    """Base class for exceptions raised by actions."""

    kind = "danger"
    status_int = 400  # HTTP response code indicating invalid request

    def __init__(self, status_int: int=400, title: str="", plain: str="",
                 html: str="", kind: str="danger") -> None:
        """Constructor."""
        Returnable.__init__(self)
        self.status_int = status_int
        if title or plain or html:
            self.add_message(
                title=title, kind=kind, plain=plain, html=html)
        self.invalid = {}  # type: Dict[str, Any]


@to_dict.register(obj=MalbonaRezulto, flavor='')
def malbona_to_dict(obj, flavor='', **kw):
    """Convert a MalbonaRezulto to a dictionary."""
    amap = returnable_to_dict(obj=obj, flavor='', **kw)
    amap['invalid'] = obj.invalid
    return amap
