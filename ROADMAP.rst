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


Ideas for kerno.email
=====================

- Address class -- does pyramid_mailer have it?
- Envelope class -- does anyone have it?
- Message class
- Registry for a function that sends out an email
- Implementation that sends it immediately
- Implementation that sends it through Celery
- Implementation that only tests it

Desired mailer features:

- Templates
- validates input
- holds configuration for SMTP credentials, default sender
- premailer somehow (to use CSS in templates)
- no need for transports, because Celery
- DummyMailer for tests

kerno utilities:

def message_maker(envelope, html, plain)
def email_sender(envelope, msg)

Envelope(subject, author=None, plain=None, rich=None,
             to=None, cc=None, bcc=None, reply=None)
