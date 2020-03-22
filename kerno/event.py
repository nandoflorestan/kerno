"""A tiny event library.

Stolen from https://stackoverflow.com/questions/1092531/event-system-in-python

Typical usage::

    my_kerno_instance.my_event = Event()
    my_kerno_instance.my_event.append(my_subscriber)
    my_kerno_instance.my_event(**kwargs)
"""


class Event(list):
    """Event subscription.

    A list of callable objects. Calling an instance of this will cause a
    call to each item in the list in ascending order by index.

    Example usage::

        >>> def f(x):
        ...     print 'f(%s)' % x
        >>> def g(x):
        ...     print 'g(%s)' % x
        >>> e = Event()
        >>> e()
        >>> e.append(f)
        >>> e(123)
        f(123)
        >>> e.remove(f)
        >>> e()
        >>> e += (f, g)
        >>> e(10)
        f(10)
        g(10)
        >>> del e[0]
        >>> e(2)
        g(2)
    """

    def __call__(self, *args, **kwargs) -> None:
        """Broadcast this event to the subscribers in the list."""
        for fn in self:
            fn(*args, **kwargs)

    def __repr__(self) -> str:
        return "Event(%s)" % list.__repr__(self)
