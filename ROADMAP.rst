=============
Kerno roadmap
=============

These are some ideas for things the Kerno library could provide:

- Use colander to validate configuration
- Investigate https://antidote.readthedocs.io/en/latest/
- A component to register and generate URLs
- Hook documentation for the implemented actions
- Generalize mixin composition, for applications made of multiple modules:
  ``eko.add_mixin(to_assemble='repository', MyRepositoryPart)``
- Actions are composable: validator actions, then main actions, then logging.
- Register schemas: ``schemas.register(action=CreateUser, MySchema, petition)``
- Register logging functions: ``logging.register(action=CreateUser, MyLogger, petition)``
- app_name setting
- app_package setting
- modules_package setting (undocumented, default 'modules')
- modules directory
- Optional SQLAlchemy transaction integration, but at the right distance.
  For instance, research if it is possible to commit the transaction
  after an action, and still return to the controller the (now harmless)
  detached entities.
- Optional Celery integration and other services too
- Figure out how to create a WebSockets server that doesn't open many database
  connections. Maybe have a WebSockets middleware and continue to use Pyramid.
- Provide an example app or a good example in the tests.
