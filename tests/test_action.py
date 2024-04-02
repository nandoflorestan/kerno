"""Tests for kerno.action helper classes."""

from base64 import b64encode

from kerno.action import EntityComparison, OrganizeHashableObjects, OrganizeValueObjects
from kerno.entities import UploadedFile


def test_EntityComparison():  # noqa
    old = UploadedFile(filename="autoexec.bat", payload=b64encode(b"@ECHO OFF"))
    new = UploadedFile(filename="hello_world.py", payload=b64encode(b"print('hi')"))
    comparison = EntityComparison(old, new)
    assert comparison.get_differences() == [
        ("byts", b"@ECHO OFF", b"print('hi')"),
        ("filename", old.filename, new.filename),
    ]
    assert comparison.get_differences(var_names=("byts",)) == [
        ("byts", b"@ECHO OFF", b"print('hi')"),
    ]
    assert str(comparison) == (
        "byts changed from «b'@ECHO OFF'» to «b\"print('hi')\"». "
        "filename changed from «autoexec.bat» to «hello_world.py»."
    )


existing = [("existing and desired",), ("existing but not desired",)]
desired = [("existing and desired",), ("new and desired",)]


def test_OrganizeHashableObjects():  # noqa
    org = OrganizeHashableObjects(existing, desired)
    assert len(org.to_add) == 1
    assert len(org.to_keep) == 1
    assert len(org.to_remove) == 1
    assert desired[1] in org.to_add
    assert existing[0] in org.to_keep
    assert existing[1] in org.to_remove


def test_OrganizeValueObjects():  # noqa
    org = OrganizeValueObjects(existing, desired)
    assert len(org.to_add) == 1
    assert len(org.to_keep) == 1
    assert len(org.to_remove) == 1
    assert desired[1] in org.to_add
    assert existing[1] in org.to_remove
    comparison = org.to_keep[0]
    assert existing[0] is comparison.old
    assert desired[0] is comparison.new
