"""Tests for the kerno.web.to_dict module."""

from collections import OrderedDict
from unittest import TestCase
from kerno.state import to_dict, MalbonaRezulto, Rezulto, UICommand, UIMessage


class TestUIMessage(TestCase):
    """Test cases for the UIMessage class and to_dict()."""

    def _make_one(self):
        return UIMessage(title="Prokofiev is the best!",
                         plain="We like Prokofiev here.", kind="error")

    def test_ui_message_to_dict(self):
        examined = self._make_one()
        adict = to_dict(examined)
        assert isinstance(adict, OrderedDict)
        assert adict['title'] == "Prokofiev is the best!"
        assert adict['plain'] == "We like Prokofiev here."
        assert adict['html'] == ""
        with self.assertRaises(KeyError):
            adict['KINDS']

    def test_ui_message_repr(self):
        examined = self._make_one()
        astr = repr(examined)
        assert isinstance(astr, str)
        assert astr == '<UIMessage "Prokofiev is the best!">'


class TestRezulto(TestCase):
    """Test cases for the Rezulto class and to_dict()."""

    def _make_one(self):
        rez = Rezulto(commands=[UICommand(
            name='add joke',
            payload={'What does a composer do when he dies?': 'Decompose'},
        )])
        rez.add_toast(title="Prokofiev is the best!",
                      plain="We like Prokofiev here.")
        rez.redirect = '/'
        rez.debug = {'user': 'Mr. Golden Ears'}
        return rez

    def test_rezulto_to_dict(self):
        examined = self._make_one()
        adict = to_dict(examined)
        assert isinstance(adict, OrderedDict)
        assert adict['status_int'] == 200
        assert adict['kind'] == 'success'
        assert adict['messages'] == []
        assert adict['toasts'] == [OrderedDict([
            ('html', ''),
            ('kind', 'success'),
            ('plain', 'We like Prokofiev here.'),
            ('title', 'Prokofiev is the best!'),
        ])]
        assert adict['debug'] == {'user': 'Mr. Golden Ears'}
        assert adict['redirect'] == '/'
        assert adict['commands'] == [{
            'name': 'add joke',
            'payload': {'What does a composer do when he dies?': 'Decompose'},
        }]
        with self.assertRaises(KeyError):
            adict['KINDS']

    def test_rezulto_repr(self):
        examined = self._make_one()
        astr = repr(examined)
        assert isinstance(astr, str)
        assert astr == '<Rezulto status: 200>'


class TestMalbonaRezulto(TestCase):
    """Test cases for the MalbonaRezulto class and to_dict()."""

    def _make_one(self):
        rez = MalbonaRezulto(title="Prokofiev is the best!",
                             plain="We like Prokofiev here.")
        rez.redirect = '/'
        rez.debug = {'user': 'Mr. Golden Ears'}
        return rez

    def test_malbona_to_dict(self):
        examined = self._make_one()
        adict = to_dict(examined)
        assert isinstance(adict, OrderedDict)
        assert adict['status_int'] == 400
        assert adict['kind'] == 'danger'
        assert adict['toasts'] == []
        assert adict['messages'] == [OrderedDict([
            ('html', ''),
            ('kind', 'danger'),
            ('plain', 'We like Prokofiev here.'),
            ('title', 'Prokofiev is the best!'),
        ])]
        assert adict['debug'] == {'user': 'Mr. Golden Ears'}
        assert adict['redirect'] == '/'
        with self.assertRaises(KeyError):
            adict['payload']

    def test_malbona_repr(self):
        examined = self._make_one()
        astr = repr(examined)
        assert isinstance(astr, str)
        assert astr == '<MalbonaRezulto status: 400>'
