# noqa

from unittest import TestCase
from kerno.start import ConfigurationError, Eko


class TestUtilityRegistry(TestCase):  # noqa

    def _make_one(self, register=False):
        eko = Eko({})
        if register:
            eko.utilities.register('test_utility', object)
        return eko

    def test_get_returns_None_when_utility_not_registered(self):  # noqa
        eko = self._make_one()
        assert eko.kerno.utilities.get('test_utility') is None

    def test_get_returns_registered_utility(self):  # noqa
        eko = self._make_one(register=True)
        assert eko.kerno.utilities.get('test_utility') is object

    def test_ensure_returns_None_when_utility_registered(self):  # noqa
        eko = self._make_one(register=True)
        assert eko.utilities.ensure('test_utility') is None

    def test_ensure_raises_ConfigurationError_if_not_registered(self):  # noqa
        eko = self._make_one()
        with self.assertRaises(ConfigurationError):
            eko.utilities.ensure('test_utility')

    def test_set_default_does_register_missing_utility(self):  # noqa
        eko = self._make_one()
        eko.utilities.set_default('test_utility', object)
        assert eko.kerno.utilities.get('test_utility') is object

    def test_set_default_does_nothing_when_utility_present(self):  # noqa
        eko = self._make_one(register=True)
        eko.utilities.set_default('test_utility', eko)
        assert eko.kerno.utilities.get('test_utility') is object  # and not eko

    def test_utilities_immutable_after_startup(self):  # noqa
        eko = self._make_one(register=True)
        with self.assertRaises(TypeError):
            eko.kerno.utilities['cannot assign'] = object
