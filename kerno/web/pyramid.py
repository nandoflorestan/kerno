"""Integration between Kerno and the awesome Pyramid web framework."""

from functools import wraps
from typing import Callable
from kerno.state import MalbonaRezulto, Rezulto, to_dict
from zope.interface import Interface


class IKerno(Interface):
    """Marker to register and retrieve a Kerno instance in a Pyramid app."""


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
    return context.to_dict()


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
