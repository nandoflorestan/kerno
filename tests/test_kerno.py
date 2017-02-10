from unittest import TestCase
from kerno.core import Kerno


class TestUtilityRegistry(TestCase):

    def _make_one(self, register=False):
        k = Kerno({})
        if register:
            k.register_utility('test_utility', object)
        return k

    def test_get_utility_returns_None_when_utility_not_registered(self):
        kerno = self._make_one()
        assert kerno.get_utility('test_utility') is None

    def test_get_utility_returns_registered_utility(self):
        kerno = self._make_one(register=True)
        assert kerno.get_utility('test_utility') is object

    def test_ensure_utility_returns_None_when_utility_registered(self):
        kerno = self._make_one(register=True)
        assert kerno.ensure_utility('test_utility') is None

    def test_ensure_utility_raises_RuntimeError_if_not_registered(self):
        kerno = self._make_one()
        with self.assertRaises(RuntimeError):
            kerno.ensure_utility('test_utility')

    def test_set_default_utility_does_register_missing_utility(self):
        kerno = self._make_one()
        kerno.set_default_utility('test_utility', object)
        assert kerno.get_utility('test_utility') is object

    def test_set_default_utility_does_nothing_when_utility_present(self):
        kerno = self._make_one(register=True)
        kerno.set_default_utility('test_utility', kerno)
        assert kerno.get_utility('test_utility') is object  # and not kerno
