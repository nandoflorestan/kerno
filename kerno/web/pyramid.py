"""Integration between Kerno and the awesome Pyramid web framework."""

from functools import wraps
import inspect
from typing import Any, Callable, Dict

from kerno.action import Action
from kerno.state import MalbonaRezulto, Rezulto, to_dict
from zope.interface import Interface


class IKerno(Interface):
    """Marker to register and retrieve a Kerno instance in a Pyramid app."""


def _from_pyramid(cls, request):
    """Conveniently instantiate a kerno action from a Pyramid view."""
    return cls(kerno=request.kerno,
               user=request.user,
               repo=request.repo)


# Monkeypatch the Action class so it has a ._from_pyramid(request) classmethod
Action.from_pyramid = classmethod(_from_pyramid)  # type: ignore


def kerno_view(fn: Callable) -> Callable:
    """Decorate Pyramid views that call Kerno actions or operations.

    The view can return a Rezulto or RAISE a MalbonaRezulto. Then this
    decorator sets the status_int of the response (to 200 or 201) and
    converts it to a dictionary.
    """
    args = inspect.getargspec(fn).args
    if len(args) == 1 and 'self' == args[0]:       # view signature #1: self
        def get_request(args):
            return args[0].request
    elif len(args) == 1 and 'request' == args[0]:  # view signature #2: request
        def get_request(args):
            return args[0]
    elif len(args) == 2 and 'request' == args[1]:  # view signature #3:
        def get_request(args):                     # context, request
            return args[1]
    else:
        raise RuntimeError('The kerno_view decorator found an '
                           'unexpected signature in {}'.format(fn))

    @wraps(fn)
    def wrapper(*args):
        rezulto = fn(*args)
        if isinstance(rezulto, Rezulto):
            request = get_request(args)
            request.response.status_int = rezulto.status_int
            return to_dict(obj=rezulto)
        else:
            return rezulto

    return wrapper


def malbona_view(context, request) -> Dict[str, Any]:
    """Pyramid view handler that returns a MalbonaRezulto as a dictionary."""
    request.response.status_int = context.status_int
    return to_dict(context)


def includeme(config) -> None:
    """Add our views to a Pyramid app so it will display our exceptions.

    For the HTML version, if you'd like to change our template to your own,
    just override the Pyramid view configuration. Example::

        config.add_view(
            context=MalbonaRezulto, accept='text/html', view=malbona_view,
            renderer='yourapp:templates/malbona.jinja2')
    """
    config.add_view(
        context=MalbonaRezulto, accept='text/html', view=malbona_view,
        renderer='kerno:web/malbona.jinja2')
    config.add_view(
        context=MalbonaRezulto, renderer='json', view=malbona_view,
        accept='application/json')
    config.add_view(
        context=MalbonaRezulto, renderer='json', view=malbona_view, xhr=True)
    config.add_request_method(  # request.kerno is computed once per request
        lambda request: request.registry.getUtility(IKerno),
        'kerno', reify=True)
