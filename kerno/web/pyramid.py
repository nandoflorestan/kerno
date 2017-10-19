"""Integration between Kerno and the awesome Pyramid web framework."""

from functools import wraps
from kerno.state import Peto, Rezulto, MalbonaRezulto
from zope.interface import Interface


class IKerno(Interface):
    """Marker to register and retrieve a Kerno instance in a Pyramid app."""


def kerno_view(fn):
    """Decorate Pyramid views that call Kerno actions or operations.

    The view should return a Peto or a Rezulto. Then this decorator sets the
    status_int of the response (to 200 or 201) and converts to dict.
    """
    @wraps(fn)
    def wrapper(request):
        rez = fn(request)
        if isinstance(rez, Peto):
            rezulto = rez.rezulto
        elif isinstance(rez, Rezulto):
            rezulto = rez
        else:
            return rez
        request.response.status_int = rezulto.status_int
        return rezulto.to_dict()

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
