"""Integration between Kerno and the awesome Pyramid web framework."""

from functools import wraps
import inspect
from json import dumps
from typing import Callable

from bag.web.exceptions import Problem
from zope.interface import Interface

from kerno.kerno import Kerno
from kerno.state import MalbonaRezulto, Rezulto, to_dict
from .typing import DictStr, KRequest


def kerno_view(fn: Callable) -> Callable:
    """Decorate Pyramid views that call Kerno actions or operations.

    The view can return a Rezulto or RAISE a MalbonaRezulto. Then this
    decorator sets the status_int of the response (to 200 or 201) and
    converts it to a dictionary.
    """
    args = [str(name) for name in inspect.signature(fn).parameters.keys()]
    if len(args) == 1 and "self" == args[0]:  # view signature #1: self

        def get_request(args):
            return args[0].request

    elif len(args) == 1 and "request" == args[0]:  # view signature #2: request

        def get_request(args):
            return args[0]

    elif len(args) == 2 and "request" == args[1]:  # view signature #3:

        def get_request(args):  # context, request
            return args[1]

    else:
        raise RuntimeError(
            f"The kerno_view decorator found an unexpected signature in {fn}"
        )

    @wraps(fn)
    def wrapper(*args):
        try:
            rezulto = fn(*args)
        except Problem as e:
            adict = e.to_dict()
            raise MalbonaRezulto(
                # content_type='application/json',
                status_int=e.status_int,
                invalid=dumps(adict),
                title=e.error_title or "Server error",
                plain=e.error_msg,  # could be shown to end users
                debug=e.error_debug,  # not displayed to end users
            )
        if rezulto is None:
            raise RuntimeError(
                "Error: None returned by view {}()".format(fn.__qualname__)
            )
        elif isinstance(rezulto, Rezulto):
            request = get_request(args)
            request.response.status_int = rezulto.status_int
            return to_dict(obj=rezulto)
        else:
            return rezulto

    return wrapper


def malbona_view(context, request) -> DictStr:
    """Pyramid view handler that returns a MalbonaRezulto as a dictionary."""
    request.response.status_int = context.status_int
    return to_dict(context)


def raise_if_not_authenticated(request: KRequest) -> None:
    """Return 418 if the client is not authenticated.

    The code 401 is for missing HTTP Basic Authentication and comes with
    related expectations, therefore we abuse "418 I'm a teapot"
    which was spent in a joke and therefore is never used.

    This is better than Pyramid's ``is_authenticated=True`` view predicate,
    which returns 404.

    The response includes a UIMessage and a command to show the login form.
    """
    if request.identity:
        return
    args = {
        "title": "Not authenticated",
        "plain": "The resource requires that you be logged in.",
    }
    malbona = MalbonaRezulto(status_int=418, **args)  # type: ignore[arg-type]
    malbona.add_command(name="allowLogin", payload=None)  # show login form
    malbona.add_message(level="danger", **args)
    raise malbona


class IKerno(Interface):
    """Marker to register and retrieve a Kerno instance in a Pyramid app."""


def includeme(config) -> None:
    r"""Integrate kerno with Pyramid.

    - Make ``request.kerno`` available.
    - Make ``request.repo`` available.
    - Also register an ``IKerno`` interface so one can retrieve the kerno
      instance from the Pyramid registry with
      ``kerno = registry.queryUtility(IKerno, default=None)``.
    - Add our views to a Pyramid app so it will display our exceptions.

    Usage example::

        from kerno.web.pyramid import IKerno, Kerno

        def init_kerno(config_path: str) -> Kerno:
            \"\"\"Return initialized kerno, separate from web frameworks.\"\"\"
            from kerno.start import Eko
            eko = Eko.from_ini(config_path)
            # ...more kerno initialization code here, then...
            return eko.kerno

        def main(global_config, **settings):
            \"\"\"Return a Pyramid WSGI application.\"\"\"
            from pyramid.config import Configurator
            with Configurator(settings=settings) as config:
                kerno = init_kerno(global_config['__file__'])
                config.registry.registerUtility(kerno, IKerno)
                config.include('kerno.web.pyramid')
                # ...more Pyramid configuration code here, then at the end...
            return config.make_wsgi_app()

    For the HTML version, if you'd like to change our template to your own,
    just override the Pyramid view configuration. Example::

        config.add_view(
            context=MalbonaRezulto, accept='text/html', view=malbona_view,
            renderer='yourapp:templates/malbona.jinja2')
    """
    kerno = config.registry.queryUtility(IKerno, default=None)
    if not isinstance(kerno, Kerno):
        raise RuntimeError(
            "A Kerno instance must be registered with Pyramid "
            "before including 'kerno.web.pyramid'."
        )

    config.add_request_method(  # request.kerno is computed once per request
        lambda request: request.registry.getUtility(IKerno),
        "kerno",
        reify=True,
    )

    config.add_request_method(  # request.repo is computed once per request
        lambda request: request.kerno.new_repo(), "repo", reify=True
    )

    config.registry.registerUtility(kerno, IKerno)

    config.add_view(
        context=MalbonaRezulto,
        accept="text/html",
        view=malbona_view,
        renderer="kerno:web/malbona.jinja2",
    )
    config.add_view(
        context=MalbonaRezulto,
        renderer="json",
        view=malbona_view,
        accept="application/json",
    )
    config.add_view(
        context=MalbonaRezulto, renderer="json", view=malbona_view, xhr=True
    )
