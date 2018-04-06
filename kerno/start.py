"""Eko is the class used to start a Kerno application.

It works much like initial configuration of a Pyramid app.
"""

from configparser import NoSectionError
from types import ModuleType
from typing import Any, Callable, Dict, Iterable, Union
from bag.settings import read_ini_files, resolve
from .utility_registry import UtilityRegistry

ResourceType = Union[str, ModuleType, Callable]


class Eko(UtilityRegistry):
    """At startup builds the Kerno instance for the app.

    In the Esperanto language, Eko is a noun that means "a start".
    And "eki" is a verb that means "to start".

    Example::

        from kerno.start import Eko
        eko = Eko.from_ini('main_config.ini', 'production.ini')
        eko.settings  # lets you access the merged settings from INI files
        eko.kerno  # is the Kerno instance that will be the core of the app

        eko.register_utility('mailer', 'some.package:mailer_function')
        # ...and later you can retrieve *mailer_function* by doing:
        # kerno.get_utility('mailer')

        # This finds the function some.extension.package:eki() and runs it,
        # passing it the eko configurator object:
        eko.include('some.extension.package')

        # For instance, here is how you can build a repository from 2 classes:
        eko.include('kerno.repository')  # adds add_repository_mixin() to eko
        eko.add_repository_mixin(
            'kerno.repository.sqlalchemy.BaseSQLAlchemyRepository')
        eko.add_repository_mixin('my.package:MyRepoMixinClass')
        # After this, the first time you access ``kerno.Repository``,
        # the Repository class is assembled from the mixin classes,
        # and stored for usage as kerno.Repository.
    """

    @classmethod
    def from_ini(cls, *config_files, encoding: str='utf-8'):
        """Return an instance after reading some INI file(s)."""
        return cls(settings=read_ini_files(*config_files, encoding=encoding))

    def __init__(self, settings: Dict[str, Any]={}) -> None:
        """Construct."""
        if settings and not hasattr(settings, '__getitem__'):
            raise TypeError("The *settings* argument must be dict-like. "
                            "Received: {}".format(type(settings)))
        UtilityRegistry.__init__(self, settings)

        try:
            main_config_section = settings['kerno']
        except (NoSectionError, KeyError):
            return
        for extension in main_config_section.get('includes', []):
            self.include(extension)

    def include(self, resource: ResourceType, throw: bool=True) -> None:
        """Execute a configuration callable for imperative extension."""
        # TODO log.debug('Including {}'.format(module))
        obj = resolve(resource) if isinstance(resource, str) else resource
        if isinstance(obj, ModuleType):
            try:
                fn = getattr(obj, 'eki')
            except AttributeError:
                if throw:
                    raise ConfigurationError(
                        "The module {} has no function called 'eki'.".format(
                            obj.__name__))
                else:
                    return
        else:
            fn = obj
        fn(self)

    def include_many(
        self, resources: Iterable[ResourceType], throw: bool=True,
    ) -> None:
        """Initialize multiple app modules."""
        for resource in resources:
            self.include(resource, throw=throw)


class ConfigurationError(Exception):
    """Represents an error during application startup."""
