"""Library to find and compose application modules."""

from bag.settings import resolve


def compose_class(name, mixins):
    """Return a class called ``name``, made of the bases ``mixins``."""
    bases = [resolve(mixin) if isinstance(mixin, str) else mixin
             for mixin in mixins]
    return type(name, bases, {})
