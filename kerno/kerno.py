"""The Kerno class."""

from types import MappingProxyType  # which behaves like a FrozenDict
from typing import Any, Optional

from kerno.event import EventHub
from kerno.typing import DictStr


class Kerno:
    """Core of an application, integrating decoupled resources.

    The Kerno instance is used at runtime; at startup it is instantiated by
    the "Eko" configurator.
    """

    def __init__(self, settings: dict[str, DictStr], const: Optional[DictStr] = None):
        """Construct. The ``settings`` are a dict of dicts."""
        self.settings = settings
        self.utilities: MappingProxyType[str, Any] = MappingProxyType({})
        self.const = const or {}  # The app should put global constants here
        self.events = EventHub()
