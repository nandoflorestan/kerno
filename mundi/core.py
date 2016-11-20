"""The Mundi class."""

from configparser import NoSectionError
import reg
from bag.settings import read_ini_files, resolve


class Mundi:
    """Integrates decoupled resources."""

    @classmethod
    def from_ini(cls, *config_files, encoding='utf-8'):
        """Return a Mundi instance after reading some INI file(s)."""
        return cls(settings=read_ini_files(*config_files, encoding=encoding))

    def __init__(self, settings=None):
        """The ``settings`` are a dict of dicts."""

        # The registry must be local to each Mundi instance, not static:
        @reg.dispatch(reg.match_key('name', lambda name: name))
        def get_utility(name):
            """Return a utility class, or None, according to configuration."""
            return None  # when ``name`` not registered.
        self.get_utility = get_utility

        if settings and not hasattr(settings, '__getitem__'):
            raise TypeError("The *settings* argument must be dict-like. "
                            "Received: {}".format(type(settings)))
        self.settings = settings
        self.set_up_utilities()

    def set_up_utilities(self):
        """Read the config section "Mundi utilites"; register each utility."""
        try:
            section = self.settings['Mundi utilities']
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

    def run(self, agent, action, payload):
        """Execute, as ``agent``, the ``action`` with the ``payload``."""
        obj = action(
            mundi=self,
            agent=agent,
            target_action=action,
            payload=payload
        )
        adict = obj()
        return adict
