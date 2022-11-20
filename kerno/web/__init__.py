"""
to_dict() is higher than entity level
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When we think about converting an entity to a dictionary for JSON output, we immediately think this conversion belongs in the entity, and we create a to_dict() or to_json() method in the entity class. This is architecturally incorrect, here is why.

1. Permissions
===================

Sometimes the user's permissions shape how much of that entity should be sent down the wire. (Some variables might be accessible to superusers only.) Now the to_dict() method needs access to the user's permissions, which is not code that goes into entities.

By definition, figuring out permissions requires 2 entities: the user and the object on which the user can have permissions. A user has this and that permission an a certain object.

The repository should provide access the user's permissions.
It is a fundamental service, for instance::

    peto.repo.get_division_permissions(user=user, division_id=division.id)

However, *repo* should not be passed in to the method of an entity. This would overcomplicate the entity, give it knowledge of the repository and of other entities, and probably cause a circular dependency problem.

Further, we want the permissions to be obtained only once, and then used multiple times as a request is figured out.

This goes in the architecture of each specific application. In the above example, a DivisionPeto object is needed, that contains user permissions computed only once in a request, and then can be passed to multiple places, such as multiple to_dict() calls.
Such a class should be at the base of the specific app.


2. Computations
===================

Sometimes we want to push to the client the result of a calculation, as if it were a variable on the entity. If this computation needs data from outside the entity, then this code wants to stay outside the entity.


3. Trees of objects
===================

Sometimes we want to create a JSON object comprised of a sequence or a tree of entities. Evidently such code does not belong in any one of the entities involved.


Conclusion
===================

Your system may need multiple conversion behaviours for the same model -- for instance, with varying fields, verbosities, levels of detail, optional inclusion of related entities, trees of objects, certain computations etc.

To support these cases, conversion of an entity to dict or to JSON goes into a helper of actions, not into the entity.

kerno.web.jsonright provides a solution that...

1. Has a uniform signature for all to_dict() implementations, which is important to implement trees of objects.
2. Uses single dispatch. This means it behaves polymorphically depending on entity type and is only one name for the user code to import.
3. Saves bandwidth when many entities are sent to the client.
"""
