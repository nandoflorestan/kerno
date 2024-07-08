from abc import ABCMeta
from typing import TypedDict

from kerno.typing import DictStr
from bag.reify import reify


class MandatoMessage(TypedDict):
    """Type of the dictionary that a Mandato outputs."""

    name: str
    payload: DictStr | list


# Advice: refrain from generic typing here to avoid useless mypy warnings and
# a circular import issue. Subclasses can specify payload and peto types directly.
class Mandato(metaclass=ABCMeta):
    """Abstract base class for a command to be sent to the user interface.

    It is common to override the serialize_payload() method.
    """

    def __init__(self, payload, peto, **kw) -> None:
        """``payload`` is the Python data which will be serialized.

        It will then be sent to the UI and be the input to a specified command.
        ``kw`` are arguments to the ``serialize_payload`` method.
        """
        self.payload = payload
        self.peto = peto
        self.kw = kw

    @property
    def name(self) -> str:
        """Return the name of the Mandato: the corresponding UI function name.

        By default, it's the name of the Mandato subclass, starting in lowercase.
        If the Python class is named SetCurrentUser, the JS function to handle
        such a mandate would be called setCurrentUser.
        """
        name = self.__class__.__name__
        name = name[0].lower() + name[1:]
        return name

    def __repr__(self) -> str:
        return '<Mandato "{}">'.format(self.name)

    def serialize_payload(self) -> DictStr | list:
        """Implement serialization of the payload."""
        from kerno.web.jsonright import jsonright

        return jsonright(self.payload, peto=self.peto, **self.kw)

    @reify
    def as_dict(self) -> MandatoMessage:
        """Return the message as a dictionary, usually for JSON output."""
        return {"name": self.name, "payload": self.serialize_payload()}
