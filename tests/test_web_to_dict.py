"""Tests for the kerno.web.to_dict module."""

from collections import OrderedDict
from datetime import datetime
from unittest import TestCase
from kerno.web.to_dict import reuse_dict, to_dict


class MyModel:
    """We use this model to test the default to_dict() implementation only."""

    def __init__(self):
        """Construct."""
        self.name = "Nando Florestan"
        self.profession1 = "Python developer"
        self.birth = datetime(1976, 7, 18)
        self.password = "Krystian Zimerman"  # we never want passwords in JSON


class MyModelSubclass(MyModel):
    """We use this model to test 2 custom to_dict() implementations."""

    def __init__(self):
        """Construct."""
        super().__init__()
        self.profession2 = "Classical music composer"


# Here are our 2 overloaded versions of to_dict():


@to_dict.register(obj=MyModelSubclass, flavor="")
def to_dict_2(obj, flavor="", **kw):
    """Return a dict specific for MyModelSubclass."""
    keys = kw.get("keys", ("name", "profession2"))
    return reuse_dict(obj, keys=keys, **kw)


@to_dict.register(obj=MyModelSubclass, flavor="verbose")
def verbose(obj, flavor="verbose", **kw):
    """Return a VERBOSE dict specific for MyModelSubclass."""
    amap = reuse_dict(obj, **kw)
    # This version includes even the class name:
    amap["__class__"] = MyModelSubclass.__name__
    return amap


class TestDefaultToDictImplementation(TestCase):
    """Test cases for our default to_dict() implementation."""

    def test_to_dict_plainly(self):
        entity = MyModel()
        adict = to_dict(entity)
        assert isinstance(adict, OrderedDict)
        assert adict["name"] == "Nando Florestan"
        assert adict["profession1"] == "Python developer"
        assert adict["birth"] == "1976-07-18T00:00:00"  # a string!
        with self.assertRaises(KeyError):
            adict["password"]

    def test_to_dict_with_keys(self):
        entity = MyModel()
        adict = to_dict(entity, keys=["name"])
        assert isinstance(adict, OrderedDict)
        assert adict["name"] == "Nando Florestan"
        with self.assertRaises(KeyError):
            adict["birth"]
        with self.assertRaises(KeyError):
            adict["password"]

    def test_to_dict_not_for_json(self):
        entity = MyModel()
        adict = to_dict(entity, for_json=False)
        assert isinstance(adict, OrderedDict)
        assert adict["name"] == "Nando Florestan"
        assert adict["profession1"] == "Python developer"
        assert adict["birth"] == datetime(1976, 7, 18)  # not a string
        with self.assertRaises(KeyError):
            adict["profession2"]
        with self.assertRaises(KeyError):
            adict["password"]


class TestCustomToDictImplementation(TestCase):
    """Test cases for our overloaded to_dict() implementations."""

    def test_to_dict_2(self):
        entity = MyModelSubclass()
        adict = to_dict(entity)
        assert isinstance(adict, OrderedDict)
        assert adict["name"] == "Nando Florestan"
        assert adict["profession2"] == "Classical music composer"
        with self.assertRaises(KeyError):
            adict["birth"]  # because we defined a custom key list
        with self.assertRaises(KeyError):
            adict["__class__"]
        with self.assertRaises(KeyError):
            adict["password"]

    def test_verbose(self):
        entity = MyModelSubclass()
        adict = to_dict(entity, flavor="verbose")
        assert isinstance(adict, OrderedDict)
        assert adict["name"] == "Nando Florestan"
        assert adict["profession2"] == "Classical music composer"
        assert adict["profession1"] == "Python developer"
        assert adict["birth"] == "1976-07-18T00:00:00"  # a string!
        assert adict["__class__"] == "MyModelSubclass"
        with self.assertRaises(KeyError):
            adict["password"]
