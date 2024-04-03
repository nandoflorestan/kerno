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


def test_organize_tuples():
    """Ensure tuples are correctly classified into to_add, to_keep, to_remove."""
    org = OrganizeValueObjects(existing, desired)
    assert len(org.to_add) == 1
    assert len(org.to_keep) == 1
    assert len(org.to_remove) == 1
    assert desired[1] in org.to_add
    assert existing[1] in org.to_remove
    comparison = org.to_keep[0]
    assert existing[0] is comparison.old
    assert desired[0] is comparison.new
    assert len(org.updated) == 0


def test_organize_entities():  # noqa
    old = UploadedFile(filename="hello_world.py", payload=b64encode(b"@ECHO OFF"))
    new = UploadedFile(filename="hello_world.py", payload=b64encode(b"print('hi')"))
    org = OrganizeValueObjects(
        [old], [new], eq_fn=lambda one, other: one.filename == other.filename
    )
    assert repr(org) == "<OrganizeValueObjects add:0 keep:1 del:0>"
    comparison = org.to_keep[0]
    assert old is comparison.old
    assert new is comparison.new

    # Test the method that updates kept objects with desired variables:
    assert len(org.updated) == 0
    org.update_kept_entities(var_names=("byts",))
    assert len(org.updated) == 1
    assert org.updated[0] is old
    assert org.updated[0].byts is new.byts
