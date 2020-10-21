"""A tiny event library.

Typical usage::

    # First a library defines an event class to contain event data:

    from kerno.event import KernoEvent

    class EventUserLoggedIn(KernoEvent):
        def __init__(self, peto):
            self.peto = peto
            # ...and other data that user code might find important.

    # The library can trigger the example event by doing:
    EventUserLoggedIn(peto).broadcast()  # call all subscribers

    # Elsewhere, user code will import the event class and write a handler:
    from example_library import EventUserLoggedIn

    @EventUserLoggedIn.subscribe
    def when_user_logs_in(event):
        print(event.peto)

    # Instead of the decorator you can subscribe imperatively:
    def when_user_logs_in(event):
        print(event.peto)
    EventUserLoggedIn.subscribe(when_user_logs_in)

    # Sometimes it is necessary to avoid leaks by unsubscribing:
    EventUserLoggedIn.unsubscribe(when_user_logs_in)
"""

from typing import Callable, List


class KernoEvent:
    """A tiny event class.  Should be subclassed to put data in constructor."""

    _subscribers: List[Callable] = []

    def broadcast(self):
        for fn in self._subscribers:
            fn(self)

    @classmethod
    def subscribe(cls, fn):
        """Subscribe a function to this event."""
        cls._subscribers.append(fn)
        return fn

    @classmethod
    def unsubscribe(cls, fn):
        """Remove a subscriber function."""
        cls._subscribers.remove(fn)
