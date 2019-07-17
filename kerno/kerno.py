"""The Kerno class."""

from types import MappingProxyType  # which behaves like a FrozenDict
from typing import Any, Dict


class Kerno:
    """Core of an application, integrating decoupled resources.

    The Kerno instance is used at runtime; at startup it is instantiated by
    the "Eko" configurator.
    """

    def __init__(self, settings: Dict[str, Dict]):
        """Construct. The ``settings`` are a dict of dicts."""
        self.settings = settings
        self.utilities: MappingProxyType[str, Any] = MappingProxyType({})
        # self.actions = ActionRegistry(kerno=self)
