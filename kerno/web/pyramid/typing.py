"""Pyramid typing stubs so we can write annotated views."""

from typing import Any, List, Optional, Union

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

    def queryUtility(self, provided, name="", default=None):
        """Retrieve a Pyramid utility."""

    def notify(self, *arg, **kw):  # TODO Fill arguments better
        """Broadcast a Pyramid event."""


class PyramidSession:
    """Typing stub for a Pyramid session object."""

    def invalidate(self) -> None:  # noqa
        ...

    def flash(self, msg, queue: str = "", allow_duplicate: bool = True) -> None:  # noqa
        ...

    def pop_flash(self) -> List[Any]:  # noqa
        ...


class PyramidResponse:
    """Typing stub for Pyramid response objects."""

    charset: str
    status: str
    status_int: int
    content_length: int
    content_type: str
    headers: DictStr
    body: bytes


class PyramidRequest:
    """Typing stub for pure Pyramid request objects."""

    method: str

    path: str
    path_info: str
    path_qs: str
    path_url: str
    url: str

    context: Any
    identity: Any  # Pyramid 2.0+
    # unauthenticated_userid: Union[int, str]  # deprecated in Pyramid 2.0
    # authenticated_userid: Union[int, str]  # deprecated in Pyramid 2.0
    # effective_principals: List[str]  # deprecated in Pyramid 2.0
    client_addr: str
    exception: Optional[Exception]

    json_body: JSON_primitives
    GET: MultiDictStub
    POST: MultiDictStub
    params: MultiDictStub
    matchdict: DictStr

    response: PyramidResponse
    registry: RegistryStub

    body: bytes
    accept_language: Any
    cookies: DictStr
    session: PyramidSession

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

    def add_flash(self, **kw) -> UIMessage:
        """Add a flash message to the current Pyramid session."""

    def get_flash_msgs(self) -> List[UIMessage]:
        """Return the UIMessages currently stored in the HTTP session."""
