"""Tests for kerno.action helper classes."""

from kerno.action import OrganizeHashableObjects, OrganizeValueObjects


def test_organizing():  # noqa
    existing = [("existing and desired",), ("existing but not desired",)]
    desired = [("existing and desired",), ("new and desired",)]
    org1 = OrganizeHashableObjects(existing, desired)
    org2 = OrganizeValueObjects(existing, desired)
    for org in (org1, org2):
        assert len(org.to_add) == 1
        assert len(org.to_keep) == 1
        assert len(org.to_remove) == 1
        assert desired[1] in org.to_add
        assert existing[0] in org.to_keep
        assert existing[1] in org.to_remove
