"""Integration between Kerno and the awesome Pyramid web framework."""

from abc import ABCMeta
from functools import wraps
from typing import Callable
from kerno.state import MalbonaRezulto, Rezulto, to_dict
from pyramid.decorator import reify
from zope.interface import Interface


class IKerno(Interface):
    """Marker to register and retrieve a Kerno instance in a Pyramid app."""


class KernoBaseView(metaclass=ABCMeta):
    """Base class for Pyramid views."""

    @reify
    def kerno(self):
        """Find the kerno instance only once."""
        return self.request.registry.getUtility(IKerno)

    @property
    def action_args(self):
        """Make it more convenient to call a kerno action.

        In your view you can call a kerno action like this::

            result = MyAction(payload, **self.action_args)
        """
        return {
            'kerno': self.kerno,
            'user': self.request.user,
            'repo': self.request.repo,
        }


def kerno_view(fn: Callable):
    """Decorate Pyramid views that call Kerno actions or operations.

    The view can return a Rezulto or RAISE a MalbonaRezulto. Then this
    decorator sets the status_int of the response (to 200 or 201) and
    converts it to a dictionary.
    """
    @wraps(fn)
    def wrapper(request):
        rezulto = fn(request)
        if isinstance(rezulto, Rezulto):
            request.response.status_int = rezulto.status_int
            return to_dict(obj=rezulto)
        else:
            return rezulto

    return wrapper


def malbona_view(context, request):
    """Pyramid view handler that returns a MalbonaRezulto as a dictionary."""
    request.response.status_int = context.status_int
    return to_dict(context)


def includeme(config):
    """Add our views to a Pyramid app so it will display our exceptions.

    For the HTML version, if you'd like to change our template to your own,
    just override the Pyramid view configuration. Example::

        config.add_view(
            context=MalbonaRezulto, accept='text/html', view=malbona_view, renderer='yourapp:templates/malbona.jinja2')
    """
    config.add_view(
        context=MalbonaRezulto, accept='text/html', view=malbona_view,
        renderer='kerno:web/malbona.jinja2')
    config.add_view(
        context=MalbonaRezulto, renderer='json', view=malbona_view,
        accept='application/json')
    config.add_view(
        context=MalbonaRezulto, renderer='json', view=malbona_view, xhr=True)
