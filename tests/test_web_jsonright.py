"""Tests for the kerno.web.jsonright module."""

from datetime import datetime
from unittest import TestCase

from kerno.typing import DictStr
from kerno.web.jsonright import entity2dict, jsonright


class TestDefaultJsonrightImplementation(TestCase):
    """Test cases for our default jsonright() implementation."""

    def test_str(self):  # noqa
        assert jsonright("Adam Harasiewicz", None) == "Adam Harasiewicz"

    def test_int(self):  # noqa
        assert jsonright(42, None) == 42

    def test_float(self):  # noqa
        assert jsonright(3.1415, None) == 3.1415

    def test_bool(self):  # noqa
        assert jsonright(False, None) is False

    def test_datetime(self):  # noqa
        assert (
            jsonright(datetime(2020, 9, 27, 4, 55, 42), None) == "2020-09-27T04:55:42"
        )

    def test_dict(self):  # noqa
        assert jsonright({"id": 1, "date": datetime(2020, 9, 27)}, None) == {
            "id": 1,
            "date": "2020-09-27T00:00:00",
        }

    def test_tuple_of_dicts(self):  # noqa
        assert jsonright(({"id": 1, "date": datetime(2020, 9, 27)},), None) == [
            {
                "id": 1,
                "date": "2020-09-27T00:00:00",
            }
        ]

    def test_frozenset(self):  # noqa
        assert jsonright(frozenset((1, 2)), None) == [1, 2]


class MyModel:  # noqa
    def __init__(self):  # noqa
        self.name = "Nando Florestan"
        self.profession1 = "Python developer"
        self.birth = datetime(1976, 7, 18)
        self.password = "Krystian Zimerman"  # we never want passwords in JSON


@jsonright.register(MyModel)
def _(obj, peto, features=(), **kw) -> DictStr:
    if "MyModel unsafe" in features:
        return entity2dict(obj, keys=["name", "password"])
    else:
        return entity2dict(obj)


class TestMyModel(TestCase):  # noqa
    def test_mymodel(self):  # noqa
        entity = MyModel()
        right = jsonright(entity, None)
        assert isinstance(right, dict)
        assert right["name"] == "Nando Florestan"
        assert right["profession1"] == "Python developer"
        assert right["birth"] == "1976-07-18T00:00:00"
        with self.assertRaises(KeyError):
            right["password"]

    def test_mymodel_unsafe(self):  # noqa
        entity = MyModel()
        right = jsonright(entity, None, features=("MyModel unsafe",))
        assert isinstance(right, dict)
        assert right["name"] == "Nando Florestan"
        assert right["password"] == "Krystian Zimerman"
        with self.assertRaises(KeyError):
            right["birth"]
        with self.assertRaises(KeyError):
            right["profession1"]


class MyModelSubclass(MyModel):  # noqa
    def __init__(self):  # noqa
        super().__init__()
        self.profession2 = "Classical music composer"


@jsonright.register(MyModelSubclass)
def _(obj, peto, features=(), **kw) -> DictStr:
    amap = entity2dict(obj)
    # This version includes even the class name:
    amap["__class__"] = MyModelSubclass.__name__
    return amap


class TestMyModelSubclass(TestCase):  # noqa
    def test_subclass(self):  # noqa
        entity = MyModelSubclass()
        right = jsonright(entity, None)
        assert isinstance(right, dict)
        assert right["name"] == "Nando Florestan"
        assert right["birth"] == "1976-07-18T00:00:00"
        assert right["profession1"] == "Python developer"
        assert right["profession2"] == "Classical music composer"
        assert right["__class__"] == "MyModelSubclass"
        with self.assertRaises(KeyError):
            right["password"]


class TestListOfEntities(TestCase):  # noqa
    def test_sequence(self):  # noqa
        payload = [MyModel()]
        right = jsonright(payload, None)
        assert isinstance(right, list)
        assert right == [
            ["name", "Nando Florestan"],
            ["profession1", "Python developer"],
            ["birth", "1976-07-18T00:00:00"],
        ]
