"""A tiny event hub.

``kerno.events`` will be an instance of EventHub, however you can also
use the EventHub class in other circumstances if you want to.

First a library defines an event class to contain event data::

    class EventUserLoggedIn:
        def __init__(self, peto):
            self.peto = peto
            # ...and other data that user code might find important.

Elsewhere, user code will import the event class and write a handler::

    from example_library import EventUserLoggedIn

    def when_user_logs_in(event: EventUserLoggedIn):
        print(event.peto)

Finally, in setup code::

    kerno.events.subscribe(EventUserLoggedIn, when_user_logs_in)

Sometimes it is necessary to avoid leaks by unsubscribing::

    kerno.events.unsubscribe(EventUserLoggedIn, when_user_logs_in)

One of the advantages of having the event hub as a separate object is
that, instead of unsubscribing many handlers, sometimes you can just
throw away the hub, replacing its instance.

The library fires the event by doing::

    kerno.events.broadcast(EventUserLoggedIn(peto=peto))
"""

from typing import Callable, Dict, List


class EventHub:
    """A hub for events to be subscribed, fired and removed."""

    def __init__(self) -> None:  # noqa
        self._events: Dict[type, List[Callable]] = {}

    def subscribe(self, event_cls: type, function: Callable) -> Callable:
        """Subscribe a handler ``function`` to the ``event_cls``."""
        assert isinstance(event_cls, type)
        assert callable(function)
        handlers: List[Callable] = self._events.setdefault(event_cls, [])
        if function in handlers:
            raise RuntimeError(
                f"This function is already subscribed to {event_cls}."
            )
        handlers.append(function)
        return function

    def unsubscribe(self, event_cls: type, function: Callable) -> bool:
        """Remove a function.  Return True if it really was subscribed."""
        handlers: List[Callable] = self._events.setdefault(event_cls, [])
        ret = function in handlers
        if ret:
            handlers.remove(function)
        return ret

    def broadcast(self, event) -> None:
        """Trigger/fire ``event`` -- execute its subscribers.

        The type of ``event`` must be an exact match: inheritance
        is not supported.
        """
        handlers: List[Callable] = self._events.setdefault(type(event), [])
        for fn in handlers:
            fn(event)
