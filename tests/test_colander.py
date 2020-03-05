"""Tests for the kerno.colander module."""

from unittest import TestCase
from unittest.mock import Mock
from kerno.colander import c, InvalidToMalbona
from kerno.state import to_dict, MalbonaRezulto, Rezulto, UICommand, UIMessage


class TestInvalidToMalbona(TestCase):
    """Test cases for the InvalidToMalbona context manager."""

    def test_no_exception(self):  # noqa
        with InvalidToMalbona(title="The title", plain="Plain text"):
            1

    def test_invalid_converts_to_malbona(self):
        with self.assertRaises(MalbonaRezulto) as e:
            with InvalidToMalbona(title="The title", plain="Plain text"):
                raise c.Invalid(Mock(), "Some validation error.")
        assert isinstance(e.exception, MalbonaRezulto)
        assert e.exception.status_int == 400
        assert e.exception.commands == []
        assert e.exception.messages == []
        assert isinstance(e.exception.toasts[0], UIMessage)
        assert isinstance(e.exception.invalid, dict)
        assert e.exception.level == "danger"
