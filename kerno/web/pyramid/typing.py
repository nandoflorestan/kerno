"""Pyramid typing stubs so we can write annotated views."""

from typing import Any, List, Union

from kerno.kerno import Kerno
from kerno.repository.sqlalchemy import BaseSQLAlchemyRepository
from kerno.state import UIMessage
from kerno.typing import DictStr


JSON_primitives = Union[DictStr, List[Any], str, int, float]


class MultiDictStub(dict):
    """Typing stub for webob.multidict.MultiDict."""

    def getall(self, key: str) -> List[JSON_primitives]:
        """Return a list of all values matching key (may be an empty list)."""

    def getone(self, key: str) -> JSON_primitives:
        """Get one value matching the key. May raise KeyError."""


class RegistryStub:  # zope/interface/registry.py
    """Typing stub for a Pyramid registry object."""

    settings: DictStr

    def registerUtility(
        self,
        component=None,
        provided=None,
        name="",
        info="",
        event=True,
        factory=None,
    ):
        """Register a Pyramid utility."""

    def getUtility(self, provided, name=""):
        """Retrieve a Pyramid utility."""

    def queryUtility(self, provided, name='', default=None):
        """Retrieve a Pyramid utility."""

    def notify(*arg, **kw):  # TODO Fill arguments better
        """Broadcast a Pyramid event."""


class PyramidRequest:
    """Typing stub for pure Pyramid request objects."""

    method: str
    path: str
    context: Any

    json_body: JSON_primitives
    GET: MultiDictStub
    POST: MultiDictStub
    params: MultiDictStub
    matchdict: DictStr

    response: object  # so we can stub this later when mypy complains
    registry: RegistryStub

    body: bytes
    accept_language: Any
    cookies: DictStr
    session: object  # so we can stub this later when mypy complains

    def route_path(self, route_name: str, *elements, **kw) -> str:
        """Generate a relative URL for a named Pyramid route."""

    def static_path(self, path: str, **kw) -> str:
        """Generate a relative URL to a static resource."""


class KRequest(PyramidRequest):
    """Typing stub for a Pyramid/kerno request object.

    It is recommended that you subclass with a more specific
    typing annotation for the ``user`` instance variable.
    """

    kerno: Kerno
    repo: BaseSQLAlchemyRepository
    user: Any

    def add_flash(request, allow_duplicate: bool = False, **kw) -> UIMessage:
        """Add a flash message to the current Pyramid session."""
