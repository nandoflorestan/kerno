=============
Kerno roadmap
=============

Because Kerno is so young, this document is a mess. Do not
read it now; I'll tidy it up in the future.

- Figure out how to create a WebSockets server that doesn't open many database
  connections. Maybe have a WebSockets middleware and continue to use Pyramid.
- Provide an example app or a good example in the tests.
- Investigate https://antidote.readthedocs.io/en/latest/
- Generalize mixin composition, for applications made of multiple modules:
  ``eko.add_mixin(to_assemble='repository', MyRepositoryPart)``

- Actions are composable: validator actions, then main actions, then logging.
- Register schemas: ``schemas.register(action=CreateUser, MySchema, petition)``
- Register logging functions: ``logging.register(action=CreateUser, MyLogger, petition)``
- app_name setting
- app_package setting
- modules_package setting (undocumented, default 'modules')
- modules directory
- A component to register and generate URLs. Alternatively, explain to me how
  URL generation can be left to the controller layer outside of this project.
  I don't think it can.
- Hook documentation for the implemented actions
- Optional SQLAlchemy transaction integration, but at the right distance.
  For instance, research if it is possible to commit the transaction
  after an action, and still return to the controller the (now harmless)
  detached entities.
- Optional Celery integration and other services too

Ideas:

- Validation for input structures could be registered.
  Because validation libraries raise their own exceptions, a couple choices, such as...

- colander and
- https://github.com/keleshev/schema

...might be integrated into the framework as examples.

Instead of get_utility(SASession) I can just use a dictionary-registry, but for adaptation I need a plugin framework:

- pyramid_mailer_message
- app_mailer_task
- marrow_message : IMessage

	registry.add_adapter(adapter_fn)

	@celery_task
	def send_email(message):
		# Could return message itself or an adapter:
		desired_message = component_framework.adapt(pyramid_mailer_message, IMessage)
