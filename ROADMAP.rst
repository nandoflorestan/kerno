=============
Kerno roadmap
=============

- Operation registry
- Maybe the action is easier to test if it suffers automatic dependency injection?
- ValidatingOperation adds ValidationAction before the main action.
- A start procedure in which plugins (the modules of the system) are found
  and initialized. Start with the repository.
- mixin composition, for applications made of multiple modules:
  ``config.add_mixin(to_assemble='repository', MyRepositoryPart)``
- Actions are composable: validator actions, then main actions, then logging.
- Register schemas: ``schemas.register(action=CreateUser, MySchema, petition)``
- Register logging functions: ``logging.register(action=CreateUser, MyLogger, petition)``
- Actions are undoable: Command, History
- A good scheme to communicate with the web framework of choice. This might
  include good Exception classes, or just a convention for the returned objects.
- Optional Pyramid integration with total decoupling. Integration could mean,
  for instance, just something that renders our exceptions into responses.
- action interface
- strategies
  - operation logging
  - storage
    - sqlalchemy
      - Automatically imports modules' storage_sqlalchemy.py and composes
      the final Repository class out of mixins.
- app_name setting
- app_package setting
- The Repository strategy is a plugin and it is dependency-injected according to
  configuration, making it easy to create a FakeRepository for fast unit testing.
- modules_package setting (undocumented, default 'modules')
- modules directory
- keepluggable as a plugin?
- burla, to register and generate URLs. Alternatively, explain to me how
  URL generation can be left to the controller layer outside of this project.
  I don't think it can.
- Hook documentation for the implemented actions
- Optional SQLAlchemy integration, but at the right distance.
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
