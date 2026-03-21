"""Base implementations that you may want to extend. See protocols.py first."""

from dataclasses import dataclass
from types import MappingProxyType  # which behaves like a FrozenDict
from typing import Any, Callable, Generic, Iterable, Type, TypeVar, Protocol, Self

from kerno.protocols import IConfig, IKerno, IPeto, IUserlessPeto, IEmailUser, IRepo
from kerno.state import MalbonaRezulto
from kerno.typing import DictStr


class Kerno(IKerno):
    """Core of an application, integrating decoupled resources.

    The Kerno instance is used at runtime; at startup it is instantiated by
    the "Eko" configurator.
    """

    def __init__(self, config: IConfig, const: DictStr | None):
        """Construct. The `config` parameter is a validated configuration object."""
        # The `settings` dictionary has been replaced by a `config` object.
        self.config = config
        self.utilities: MappingProxyType[str, Any] = MappingProxyType({})
        self.const = const or {}  # The app should put global constants here
        # self.events = EventHub()  # from kerno.event import EventHub


def _pyramid_args(request, json: bool) -> DictStr:  # noqa
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
        raw = {}
    return {
        "kerno": request.kerno,
        "repo": request.repo,
        "raw": raw,
    }


@dataclass
class UserlessPeto(IUserlessPeto):
    """Convenience type for actions NOT done by a logged user.

    An application should subclass this to replace variable types.
    """

    kerno: IKerno  # the global application object
    repo: IRepo  # the data access layer
    raw: DictStr  # operation-specific data

    @classmethod
    def from_pyramid(cls: Type["UserlessPeto"], request, json=False) -> "UserlessPeto":
        """Integration with the *pyramid* web framework.

        Typical usage is, inside your pyramid view, you do::

            upeto = UserlessPeto.from_pyramid(request, json=True)
            # Call your action/service layer, which returns a Rezulto instance:
            rezulto = create_user(upeto)
            return rezulto

        When invoked with ``json=True``, ``upeto.raw`` contains a dict
        with the JSON payload from the pyramid request.
        """
        return cls(**_pyramid_args(request, json))


@dataclass
class Peto(UserlessPeto, IPeto):
    """Convenience type for actions done by a logged user."""

    user: IEmailUser  # the current user requesting an operation. Not None!

    @classmethod
    def from_pyramid(cls: Type[Self], request, json=False) -> Self:
        r"""Integration with the *pyramid* web framework.

        Typical usage is, inside your pyramid view, you do::

            peto = Peto.from_pyramid(request, json=True)
            # Call your action/service layer, which returns a Rezulto instance:
            rezulto = some_action(peto)
            return rezulto

        When invoked with ``json=True``, ``peto.raw`` contains a dict
        with the JSON payload from the pyramid request.

        Another example, very brief::

            @kerno_view
            def get_audit_data(request):
                "\""Return audit data to be displayed to a superuser."\""
                return get_audits(
                    peto=Peto.from_pyramid(request), **request.json_body)

        This class should be used only when there is a user object, so
        this class method raises Forbidden if request.identity is None.
        You can use Pyramid to catch Forbidden and do something else --
        usually forward the user to the login form.
        """
        user = request.identity  # from a Pyramid 2.0+ security policy
        if user is None:
            # 2023-08: pyramid lacks py.typed
            from pyramid.exceptions import Forbidden  # type: ignore[import]

            raise Forbidden(
                detail="You need to log in before you can access that resource."
            )
        return cls(user=user, **_pyramid_args(request, json))

    @classmethod
    def from_userless(cls: Type[Self], upeto: UserlessPeto, user: IEmailUser) -> Self:
        """Get a Peto instance from a UserlessPeto and a user object."""
        return cls(kerno=upeto.kerno, repo=upeto.repo, raw=upeto.raw, user=user)
