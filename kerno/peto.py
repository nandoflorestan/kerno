# noqa

from dataclasses import dataclass
from typing import Any, Optional, Type, TypeVar

from kerno.kerno import Kerno
from kerno.repository.sqlalchemy import BaseSQLAlchemyRepository
from kerno.state import MalbonaRezulto
from kerno.typing import DictStr

# A generic variable that can be Peto or any subclass
APeto = TypeVar("APeto", bound="Peto")


@dataclass
class Peto:
    """An object to store incoming state.

    A Peto is typically instantiated in the controller layer and then
    passed around (as the main context object) to actions, event handlers,
    schemas, helpers etc.  This saves you from lots of boilerplate,
    removes global variables and makes unit testing easier.

    Look at the code for this class as an example.  It is recommended that
    you subclass with more concrete typing annotations.
    For instance, use static typing for the ``user`` variable.
    """

    kerno: Kerno  # the global application object
    repo: BaseSQLAlchemyRepository  # data access layer
    user: Any = None  # the current user requesting an operation
    raw: Optional[DictStr] = None  # dictionary of operation-specific data

    @classmethod
    def from_pyramid(cls: Type[APeto], request, json=False) -> APeto:
        r"""Integration with the *pyramid* web framework.

        This comes free of any pyramid imports.

        Typical usage is, inside your pyramid view, you do::

            peto = Peto.from_pyramid(request, json=True)
            # Call your action/service layer, which returns a Rezulto instance:
            rezulto = create_user(peto)
            return rezulto

        Use the ``json`` flag to obtain the payload from the pyramid request.

        Another example, very brief::

            @kerno_view
            def get_audit_data(request):
                "\""Return audit data to be displayed to a superuser."\""
                return get_audits(
                    peto=Peto.from_pyramid(request), **request.json_body)
        """
        if json:
            try:
                raw = request.json_body  # may raise ValueError
                # A JSON payload can have other types, but we want only dict
                assert isinstance(raw, dict)  # other types are a bad practice
            except Exception as e:
                raise MalbonaRezulto(
                    title="Malformed request!",
                    plain="The server could not decode the request as JSON!",
                    error_debug=str(e),
                )
        else:
            raw = None
        return cls(
            kerno=request.kerno,
            repo=request.repo,
            user=request.user,
            raw=raw,
        )
