"""Eko is the class used to start a Kerno application.

It works much like initial configuration of a Pyramid app.
"""

from configparser import NoSectionError
from importlib import import_module
from types import ModuleType
from typing import Callable, Iterable, Union

from bag.settings import read_ini_files

from kerno.kerno import Kerno
from kerno.typing import DictStr
from kerno.utility_registry import ConfigurationError, UtilityRegistryBuilder


def resolve_module(spec: str | ModuleType) -> ModuleType:
    """Return the module referred to in the ``spec`` string.

    Example spec: ``"my.python.module"``.
    """
    if not isinstance(spec, str):
        assert isinstance(spec, ModuleType), "Want a string or Python module"
        return spec
    assert spec, "Got an empty string as a spec!"
    return import_module(spec)


class Eko:
    r"""At startup builds the Kerno instance for the app.

    In the Esperanto language, Eko is a noun that means "a start".
    And "eki" is a verb that means "to start".

    The Eko class can build an application core from multiple Python modules,
    much like the Configurator in Pyramid.

    If the same module is included twice, Eko will raise
    ``kerno.start.ConfigurationError``, helping you ensure
    your startup code stays clean.

    Usage example::

        from kerno.start import Eko
        eko = Eko.from_ini('main_config.ini', 'production.ini')
        eko.settings  # lets you access the merged settings from INI files
        eko.kerno  # is the Kerno instance that will be the core of the app

        eko.utilities.register('mailer', 'some.package:mailer_function')
        # ...and later you can retrieve *mailer_function* by doing:
        # kerno.utilities['mailer']

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

    If you need to debug the order in which modules got included, you can::

        print(*eko._included_modules, sep='\n')
    """

    @classmethod
    def from_ini(cls, *config_files, encoding: str = "utf-8"):
        """Return an instance after reading some INI file(s)."""
        return cls(settings=read_ini_files(*config_files, encoding=encoding))

    def __init__(self, settings: DictStr = {}):  # noqa
        if settings and not hasattr(settings, "__getitem__"):
            raise TypeError(
                "The *settings* argument must be dict-like. "
                "Received: {}".format(type(settings))
            )

        self._included_modules: list[ModuleType] = []
        self.kerno = Kerno(settings)
        self.utilities = UtilityRegistryBuilder(kerno=self.kerno)

        try:
            main_config_section = settings["kerno"]
        except (NoSectionError, KeyError):
            return
        for extension in main_config_section.get("includes", []):
            self.include(extension)

    def include(self, spec: str | ModuleType, throw: bool = True) -> None:
        """Execute a configuration callable for imperative extension.

        If the argument ``throw`` is True (which is the default)
        and ``resource`` does not have an ``eki()`` function,
        raise ConfigurationError.  Otherwise, ignore the current module
        and return without an error.
        """
        # TODO log.debug('Including {}'.format(spec))
        module = resolve_module(spec)
        if module in self._included_modules:
            raise ConfigurationError(f"{module} has already been included!")
        else:
            self._included_modules.append(module)

        try:
            fn = getattr(module, "eki")
        except AttributeError:
            if throw:
                raise ConfigurationError(
                    "The module {} has no function called 'eki'.".format(module)
                )
            else:
                return
        fn(self)

    def include_many(
        self, specs: Iterable[str | ModuleType], throw: bool = True
    ) -> None:
        """Initialize multiple app modules."""
        for spec in specs:
            self.include(spec, throw=throw)
