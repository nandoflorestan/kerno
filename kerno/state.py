"""Classes that store state."""

from abc import ABCMeta
from collections import OrderedDict
from typing import List, Optional

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
        assert level in self.LEVELS, (
            'Unknown message level: "{0}". '
            "Possible levels are {1}".format(level, self.LEVELS)
        )
        self.level = level
        self.title = title
        self.plain = plain
        self.html = html

    def __repr__(self) -> str:
        return '<{} "{}">'.format(self.__class__.__name__, self.title)


class UICommand:
    """Represents a message telling the UI to do something."""

    __slots__ = ("name", "payload")

    def __init__(self, name: str, payload: DictStr) -> None:
        """Construct a message to the UI.

        ``name`` is the name of a command to be performed in the UI.
        ``payload`` is the data to run the command with.
        """
        self.name = name
        self.payload = payload

    def __repr__(self):
        return '<UICommand "{}">'.format(self.name)


@to_dict.register(obj=UICommand, flavor="")
def uicommand_to_dict(obj, flavor="", **kw):
    """Convert to dict a UICommand instance."""
    return OrderedDict((("name", obj.name), ("payload", obj.payload)))


class Returnable(metaclass=ABCMeta):
    """Base class for Rezulto and for MalbonaRezulto.

    Returnable is the base class for what Actions should return. It contains:

    - messages: Grave UI messages.
    - toasts: UI messages that disappear automatically after a while.
    - commands: messages to the UI, e. g., add an entity to your models
    - debug: A dict with information that is not displayed to the end user.
    - redirect: URL or screen to redirect to.

    Subclasses overload the ``status_int`` and ``level`` static variables.
    """

    level = "danger"
    status_int = 500  # HTTP response code indicating server bug/failure

    def __init__(
        self,
        commands: List[UICommand] = None,
        debug: DictStr = None,
        redirect: str = "",
        **kw,
    ):  # noqa
        self.messages: List[UIMessage] = []
        self.toasts: List[UIMessage] = []
        self.commands = commands or []
        self.debug = debug or {}
        self.redirect = redirect
        for k, v in kw.items():
            setattr(self, k, v)

    def __repr__(self) -> str:
        return "<{} status: {}>".format(
            self.__class__.__name__, self.status_int
        )

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

    def add_command(self, **kw) -> UICommand:
        """Add to the commands for the UI to perform."""
        cmd = UICommand(**kw)
        self.commands.append(cmd)
        return cmd


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
    amap["commands"] = [to_dict(uicommand) for uicommand in obj.commands]
    return amap


class Rezulto(Returnable):
    """Well-organized successful response object.

    When your action succeeds you should return a Rezulto.
    Unsuccessful operations raise MalbonaRezulto instead.
    """

    level = "success"
    status_int = 200  # HTTP response code indicating success


class MalbonaRezulto(Returnable, Exception):
    """Base class for exceptions raised by actions."""

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


@to_dict.register(obj=MalbonaRezulto, flavor="")
def malbona_to_dict(obj, flavor="", **kw):
    """Convert a MalbonaRezulto to a dictionary."""
    amap = returnable_to_dict(obj=obj, flavor="", **kw)
    amap["invalid"] = obj.invalid
    return amap
