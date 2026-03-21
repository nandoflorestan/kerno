"""A registry to store various utilities in an application."""

from configparser import NoSectionError
from types import MappingProxyType  # behaves like a FrozenDict / frozendict
from typing import Any

from bag.settings import resolve

from kerno.bases import Kerno
from kerno.protocols import TKerno
from kerno.typing import DictStr


class ConfigurationError(Exception):
    """Represents an error during application startup."""


class UtilityRegistryBuilder:
    """Gradually builds Kerno's utility registry, which is immutable."""

    def __init__(self, kerno: TKerno):
        """Read the config section "kerno utilites"; register each utility."""
        self.kerno = kerno
        self._utilities: DictStr = {}
        self.kerno.utilities = MappingProxyType(self._utilities)

        adict = kerno.config.kerno_utilities
        for name, utility in adict.items():
            self.register(name, utility)

    def register(self, name: str, utility: Any) -> Any:
        """Register ``utility`` under ``name`` at startup for later use.

        Return the resolved function, class or object.
        """
        obj = resolve(utility) if isinstance(utility, str) else utility
        # print('Registering ', name, utility, obj)
        self._utilities[name] = obj
        return obj

    def set_default(self, name: str, utility: Any) -> Any:
        """Register ``utility`` as ``name`` only if name not yet registered."""
        if self._utilities.get(name) is None:
            return self.register(name, utility)
        else:
            return None

    def ensure(self, name: str, component: str = "The application") -> None:
        """Raise if no utility has been registered under ``name``."""
        if self._utilities.get(name) is None:
            raise ConfigurationError(
                f'{component} needs a utility called "{name}", '
                "which has not been registered."
            )
