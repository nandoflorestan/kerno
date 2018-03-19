from unittest import TestCase
from kerno.start import Eko


class TestUtilityRegistry(TestCase):

    def _make_one(self, register=False):
        eko = Eko({})
        if register:
            eko.register_utility('test_utility', object)
        return eko

    def test_get_utility_returns_None_when_utility_not_registered(self):
        eko = self._make_one()
        assert eko.kerno.get_utility('test_utility') is None

    def test_get_utility_returns_registered_utility(self):
        eko = self._make_one(register=True)
        assert eko.kerno.get_utility('test_utility') is object

    def test_ensure_utility_returns_None_when_utility_registered(self):
        eko = self._make_one(register=True)
        assert eko.ensure_utility('test_utility') is None

    def test_ensure_utility_raises_RuntimeError_if_not_registered(self):
        eko = self._make_one()
        with self.assertRaises(RuntimeError):
            eko.ensure_utility('test_utility')

    def test_set_default_utility_does_register_missing_utility(self):
        eko = self._make_one()
        eko.set_default_utility('test_utility', object)
        assert eko.kerno.get_utility('test_utility') is object

    def test_set_default_utility_does_nothing_when_utility_present(self):
        eko = self._make_one(register=True)
        eko.set_default_utility('test_utility', eko)
        assert eko.kerno.get_utility('test_utility') is object  # and not eko
