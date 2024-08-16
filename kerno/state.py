"""Classes that store outgoing state.

These are typically returned by *action* layer code to controllers.
"""
from __future__ import annotations  # allows forward references; python 3.7+
from abc import ABCMeta
from collections import OrderedDict
from copy import copy
from typing import Any, Optional, Union
from warnings import warn

from kerno.mandato import Mandato
from kerno.typing import DictStr
from kerno.web.to_dict import to_dict, reuse_dict


class UIMessage:
    """Represents a message to be displayed to the user in the UI."""

    LEVELS = ["danger", "warning", "info", "success"]
    # The default to_dict() works fine for this class.

    def __init__(
        self,
        level: str = "danger",
        title: str = "",
        plain: str = "",
        html: str = "",
    ) -> None:
        """Constructor.

        ``level`` must be one of ("danger", "warning", "info", "success").
        """
        args_are_valid = (plain and not html) or (html and not plain)
        assert args_are_valid
        if level == "error":
            level = "danger"
        assert (
            level in self.LEVELS
        ), 'Unknown message level: "{0}". ' "Possible levels are {1}".format(
            level, self.LEVELS
        )
        self.level = level
        self.title = title
        self.plain = plain
        self.html = html

    def __repr__(self) -> str:
        return '<{} "{}">'.format(self.__class__.__name__, self.title)

    def to_dict(self) -> DictStr:  # noqa
        return copy(self.__dict__)

    @classmethod
    def from_payload(cls, payload: Union[str, DictStr]) -> UIMessage:  # noqa
        if isinstance(payload, str):
            return cls(plain=payload)
        else:
            return cls(**payload)


class Mandate:  # TODO Remove this class
    """Represents a command from the server to the UI.

    Prefer the new Mandato class instead.
    """

    __slots__ = ("name", "payload")

    def __init__(self, name: str, payload: DictStr) -> None:
        """Construct a message to the UI.

        ``name`` is the name of a command to be performed in the UI.
        ``payload`` is the data to run the command with.
        """
        self.name = name
        self.payload = payload

    def __repr__(self):
        return '<Mandate "{}">'.format(self.name)


@to_dict.register(obj=Mandate, flavor="")
def mandate_to_dict(obj: Mandate, flavor: str = "", **kw) -> OrderedDict[str, Any]:
    """Convert to dict a Mandate instance."""
    return OrderedDict((("name", obj.name), ("payload", obj.payload)))


class Returnable(metaclass=ABCMeta):
    """Base class for Rezulto and for MalbonaRezulto.

    Returnable is the base class for what Actions should return. It contains:

    - messages: Grave UI messages.
    - toasts: UI messages that disappear automatically after a while.
    - commands: mandates to the UI, e. g., add an entity to your models
    - headers: HTTP headers to be added to the response.
    - transient: A dict with information for other Python code layers, but that
      is NOT sent to the GUI. Used e. g. in automated tests, to allow the test
      to see some of the state of the action.
    - debug: A dict with information that is sent to the GUI, but not intended
      for to the end user to see.
    - redirect: URL or screen to redirect to.

    Subclasses overload the ``status_int`` and ``level`` static variables.
    """

    level = "danger"
    status_int = 500  # HTTP response code indicating server bug/failure

    def __init__(
        self,
        commands: Optional[list[Mandate | Mandato]] = None,
        debug: Optional[DictStr] = None,
        transient: Optional[DictStr] = None,
        redirect: str = "",
        headers: Optional[DictStr] = None,
        **kw,
    ):  # noqa
        self.messages: list[UIMessage] = []
        self.toasts: list[UIMessage] = []
        self.commands = commands or []
        self.headers = headers or {}  # HTTP headers
        self.debug = debug or {}
        self.transient = transient or {}
        self.redirect = redirect
        for k, v in kw.items():
            setattr(self, k, v)

    def __repr__(self) -> str:
        return "<{} status: {}>".format(self.__class__.__name__, self.status_int)

    def add_message(self, level: str = "", **kw) -> UIMessage:
        """Add to the grave messages to be displayed to the user on the UI."""
        msg = UIMessage(level=level or self.level, **kw)
        self.messages.append(msg)
        return msg

    def add_toast(self, level: str = "", **kw) -> UIMessage:
        """Add to the quick messages to be displayed to the user on the UI."""
        msg = UIMessage(level=level or self.level, **kw)
        self.toasts.append(msg)
        return msg

    def add_mandate(self, **kw) -> Mandate:
        """Add a mandate: a command from the server to the UI."""
        cmd = Mandate(**kw)
        self.commands.append(cmd)
        return cmd

    def add_command(self, **kw) -> Mandate:
        warn(
            "Returnable.add_command() is deprecated; use add_mandate() instead.",
            DeprecationWarning,
        )
        return self.add_mandate(**kw)

    def add(self, thing: UIMessage | Mandato):
        """Add either a toast or a mandate."""
        if isinstance(thing, UIMessage):
            self.toasts.append(thing)
        elif isinstance(thing, Mandato):
            self.commands.append(thing)
        else:
            raise RuntimeError(f"Cannot .add({thing})")


@to_dict.register(obj=Returnable, flavor="")
def returnable_to_dict(obj, flavor="", **kw):
    """Convert instance to a dictionary, usually for JSON output."""
    amap = reuse_dict(
        obj=obj,
        keys=kw.get("keys", ("level", "status_int", "debug", "redirect")),
        sort=False,
    )
    amap["messages"] = [reuse_dict(obj=msg) for msg in obj.messages]
    amap["toasts"] = [reuse_dict(obj=msg) for msg in obj.toasts]
    amap["commands"] = mandicts = []
    for mandate in obj.commands:
        if isinstance(mandate, Mandato):
            mandicts.append(mandate.as_dict)
        else:
            mandicts.append(to_dict(mandate))
    return amap


class Rezulto(Returnable):
    """Well-organized successful response object.

    When your action succeeds you should return a Rezulto.
    Unsuccessful operations raise MalbonaRezulto instead.
    """

    level = "success"
    status_int = 200  # HTTP response code indicating success


class MalbonaRezulto(Returnable, Exception):
    """Base class for exceptions raised by actions of web apps.

    Contains enough information to be translated, in the view layer,
    to an exception specific to a web framework.
    """

    level = "danger"
    status_int = 400  # HTTP response code indicating invalid request

    def __init__(
        self,
        status_int: int = 400,
        title: str = "",
        plain: str = "",
        html: str = "",
        level: str = "danger",
        invalid: Optional[DictStr] = None,
        **kw,
    ):  # noqa
        Returnable.__init__(self, **kw)
        self.status_int = status_int
        self.invalid = invalid or {}
        if title or plain or html:
            self.add_toast(title=title, level=level, plain=plain, html=html)

    @classmethod
    def aserti(
        cls,
        condition: Any,
        status_int: int = 400,
        title: str = "",
        plain: str = "",
        html: str = "",
    ):
        """Raise MalbonaRezulto if `condition` is falsy. An assertion method."""
        if not condition:
            raise cls(status_int, title, plain, html)


@to_dict.register(obj=MalbonaRezulto, flavor="")
def malbona_to_dict(obj: MalbonaRezulto, flavor: str = "", **kw) -> DictStr:
    """Convert a MalbonaRezulto to a dictionary."""
    amap = returnable_to_dict(obj=obj, flavor="", **kw)
    amap["invalid"] = obj.invalid
    return amap


class ApiRezulto:
    """Convenient protocol between Action and View for the simplest cases."""

    def __init__(self, status_int: int, payload: DictStr, **kw):
        self.status_int = status_int
        self.payload = payload
        for k, v in kw.items():
            setattr(self, k, v)

    @classmethod
    def error(cls, status_int: int, **kw) -> ApiRezulto:
        """Convenient constructor for very simple error JSON responses.

        Avoids nesting when instantiating an ApiRezulto in the action layer.

        Example::

            return ApiRezulto.error(
                400,
                title="Missing email variable",
                plain="An email must be given in the request JSON object.",
            )
        """
        return cls(status_int, kw)

    @property
    def ok(self) -> bool:
        return self.status_int > 199 and self.status_int < 300

    def to_dict(self) -> DictStr:
        """Convert to dict for JSON consumption from other applications.

        The JSON payload will either contain an *ok* object or an *error* object.
        """
        return {"ok": self.payload} if self.ok else {"error": self.payload}
