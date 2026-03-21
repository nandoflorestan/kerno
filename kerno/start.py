"""Eko is the class used to start a Kerno application.

It works much like initial configuration of a Pyramid app.
"""

import logging

from configparser import NoSectionError
from importlib import import_module
from types import ModuleType
from typing import Callable, Generic, Iterable, Type, TypeVar

from kerno.bases import Kerno, IConfig, IKerno
from kerno.protocols import TKerno
from kerno.typing import DictStr
from kerno.utility_registry import ConfigurationError, UtilityRegistryBuilder

logger = logging.getLogger(__name__)


def resolve_module(spec: str | ModuleType) -> ModuleType:
    """Return the module referred to in the ``spec`` string.

    Example spec: ``"my.python.module"``.
    """
    if not isinstance(spec, str):
        assert isinstance(spec, ModuleType), "Want a string or Python module"
        return spec
    assert spec, "Got an empty string as a spec!"
    return import_module(spec)


class Eko(Generic[TKerno]):
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
        eko = Eko(validated_configuration_object)
        eko.kerno  # is the Kerno instance that will be the core of the app
        eko.kerno.config  # returns your validated_configuration_object

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

    def __init__(
        self, config: IConfig, const: DictStr | None, kerno_class=IKerno
    ):  # noqa
        self._included_modules: list[ModuleType] = []
        self.kerno: TKerno = kerno_class(config, const=const)
        self.utilities = UtilityRegistryBuilder(kerno=self.kerno)

    def include(self, spec: str | ModuleType, throw: bool = True) -> None:
        """Execute a configuration callable for imperative extension.

        If the argument ``throw`` is True (which is the default)
        and ``resource`` does not have an ``eki()`` function,
        raise ConfigurationError.  Otherwise, ignore the current module
        and return without an error.
        """
        logger.debug(f"Including {spec}")
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
