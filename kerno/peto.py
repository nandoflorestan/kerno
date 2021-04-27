"""Convenience types to store incoming state and remove boilerplate.

A ``Peto`` is typically instantiated in the controller layer and then
passed around (as the main context object) to actions, event handlers,
schemas, helpers etc.  This removes boilerplate, helps remove
global variables and makes unit testing easier.

A previous version had an Optional ``user`` variable in Peto,
but that led to ``assert peto.user`` in most actions.  We avoid that
by providing also a ``UserlessPeto`` class.  Now it's explicit in the type!

In your application you should subclass them like this::

    from kerno.peto import AbstractPeto, AbsUserlessPeto
    UserlessPeto = AbsUserlessPeto[Repo]  # using the concrete Repo type
    Peto = AbstractPeto[Repo, User]  # with the concrete User type

"""

from dataclasses import dataclass
from typing import Generic, Type, TypeVar

from kerno.kerno import Kerno
from kerno.repository.sqlalchemy import BaseSQLAlchemyRepository
from kerno.state import MalbonaRezulto
from kerno.typing import DictStr


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


TRepo = TypeVar("TRepo", bound=BaseSQLAlchemyRepository)


@dataclass
class AbsUserlessPeto(Generic[TRepo]):
    """Convenience type for actions NOT done by a logged user."""

    kerno: Kerno  # the global application object
    repo: TRepo  # repository is an abstraction of the data access layer
    raw: DictStr  # operation-specific data

    @classmethod
    def from_pyramid(
        cls: Type["AbsUserlessPeto"], request, json=False
    ) -> "AbsUserlessPeto":
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


TUser = TypeVar("TUser")

# A generic variable that represents AbstractPeto or any subclass.
APeto = TypeVar("APeto", bound="AbstractPeto")


@dataclass
class AbstractPeto(AbsUserlessPeto[TRepo], Generic[TRepo, TUser]):
    """Convenience type for actions done by a logged user."""

    user: TUser  # the current user requesting an operation. Not None!

    @classmethod
    def from_pyramid(cls: Type[APeto], request, json=False) -> APeto:
        r"""Integration with the *pyramid* web framework.

        Typical usage is, inside your pyramid view, you do::

            peto = Peto.from_pyramid(request, json=True)
            # Call your action/service layer, which returns a Rezulto instance:
            rezulto = create_user(peto)
            return rezulto

        When invoked with ``json=True``, ``peto.raw`` contains a dict
        with the JSON payload from the pyramid request.

        Another example, very brief::

            @kerno_view
            def get_audit_data(request):
                "\""Return audit data to be displayed to a superuser."\""
                return get_audits(
                    peto=Peto.from_pyramid(request), **request.json_body)
        """
        user = request.user
        assert user is not None
        return cls(user=user, **_pyramid_args(request, json))

    @classmethod
    def from_userless(
        cls: Type[APeto], upeto: AbsUserlessPeto, user: TUser
    ) -> APeto:
        """Get a Peto instance from a UserlessPeto and a user object."""
        return cls(
            kerno=upeto.kerno, repo=upeto.repo, raw=upeto.raw, user=user
        )
