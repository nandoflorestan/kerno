"""The Kerno class."""

from configparser import NoSectionError
import reg
from bag.settings import read_ini_files, resolve
from .operation import OperationRegistry


class UtilityRegistry:
    """Mixin that contains Kerno's utility registry."""

    def __init__(self):
        """Constructor section."""
        # The registry must be local to each Kerno instance, not static.
        # This is why we define the registry inside the constructor:
        @reg.dispatch(reg.match_key('name', lambda name: name))
        def get_utility(name):
            """Return a utility class, or None, according to configuration."""
            return None  # when ``name`` not registered.
        self.get_utility = get_utility
        self.set_up_utilities()

    def set_up_utilities(self):
        """Read the config section "Kerno utilites"; register each utility."""
        try:
            section = self.settings['Kerno utilities']
        except (NoSectionError, KeyError):
            return
        for key, val in section.items():
            self.register_utility(key, val)

    def register_utility(self, name, utility):
        """Register ``utility`` under ``name`` at startup for later use."""
        obj = resolve(utility)
        # print('Registering ', name, utility, obj)
        self.get_utility.register(lambda name: obj, name=name)

    def set_default_utility(self, name, utility):
        """Register ``utility`` as ``name`` only if name not yet registered."""
        if self.get_utility.component(name) is None:
            self.register_utility(name, utility)

    def ensure_utility(self, name, component='The application'):
        """Raise if no utility has been registered under ``name``."""
        if self.get_utility.component(name) is None:
            raise RuntimeError(
                'Configuration error: {} needs a utility called "{}" '
                'which has not been registered.'.format(component, name))


class Kerno(UtilityRegistry, OperationRegistry):
    """Core of an application, integrating decoupled resources."""

    @classmethod
    def from_ini(cls, *config_files, encoding='utf-8'):
        """Return a Kerno instance after reading some INI file(s)."""
        return cls(settings=read_ini_files(*config_files, encoding=encoding))

    def __init__(self, settings=None):
        """The ``settings`` are a dict of dicts."""
        if settings and not hasattr(settings, '__getitem__'):
            raise TypeError("The *settings* argument must be dict-like. "
                            "Received: {}".format(type(settings)))
        self.settings = settings
        UtilityRegistry.__init__(self)
        OperationRegistry.__init__(self)
