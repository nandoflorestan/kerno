"""Eko mixin that builds Kerno's utility registry."""

from configparser import NoSectionError
from typing import Any
import reg
from bag.settings import resolve
from .kerno import Kerno


class UtilityRegistry:
    """Eko mixin that builds Kerno's utility registry."""

    def __init__(self, settings) -> None:
        """Construct."""
        self.kerno = Kerno(settings)

        # The registry must be local to each Kerno instance, not static.
        # This is why we define the registry inside this constructor:

        @reg.dispatch(reg.match_key('name', lambda name: name))
        def get_utility(name):
            """Return a utility class, or None, according to configuration."""
            return None  # when ``name`` not registered.
        self.kerno.get_utility = get_utility  # type: ignore
        self.set_up_utilities()

    def set_up_utilities(self) -> None:
        """Read the config section "kerno utilites"; register each utility."""
        try:
            section = self.kerno.settings['kerno utilities']
        except (NoSectionError, KeyError):
            return
        for key, val in section.items():
            self.register_utility(key, val)

    def register_utility(self, name: str, utility: Any) -> None:
        """Register ``utility`` under ``name`` at startup for later use."""
        obj = resolve(utility)
        # print('Registering ', name, utility, obj)
        self.kerno.get_utility.register(  # type: ignore
            lambda name: obj, name=name)

    def set_default_utility(self, name: str, utility: Any) -> None:
        """Register ``utility`` as ``name`` only if name not yet registered."""
        if self.kerno.get_utility.by_args(  # type: ignore
                name).component is None:
            self.register_utility(name, utility)

    def ensure_utility(
        self, name: str, component: str='The application',
    ) -> None:
        """Raise if no utility has been registered under ``name``."""
        if self.kerno.get_utility.by_args(  # type: ignore
                name).component is None:
            raise RuntimeError(
                'Configuration error: {} needs a utility called "{}" '
                'which has not been registered.'.format(component, name))
