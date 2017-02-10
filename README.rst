=====
Kerno
=====

Kerno is trying to be:

- a framework for building applications in Python
- which approximates Robert C. Martin's
  `Clean Architecture <http://blog.8thlight.com/uncle-bob/2012/08/13/the-clean-architecture.html>`_
- by empowering a service layer (here called **Action layer**)
- and moving both persistence and UI (including web frameworks) to
  the edges of the system, while still providing ways to make
  development and automated testing easier.

The documentation is at http://docs.nando.audio/kerno/latest/


Defense of the architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the first such project in the entire Python community, which
seems so addicted to the insufficient MVC or MVT offered by common
web frameworks. Kerno does not replace these frameworks, but facilitates
creation of the top layers of an architecture that contains,
from center to border:

- **Configuration layer:** Such that all other layers have access to settings.
  Why should configuration settings be available only to the web framework???
- **Model layer:** in which you define entities (e. g. SQLAlchemy models),
  but no I/O (no session, no queries). The entities can be seen
  by all the layers below.
- **Action layer:** in which you define business rules (decisions,
  the core of your app), meaning it can import and use the models above,
  and use other utilities that are dependency-injected.
- **Repository layer:** Performs database access (e. g. queries) and is
  dependency-injected into the Action layer, making unit tests easier to write.
- **Controller layer:** Thin glue layer, the only one that imports and uses
  a web framework or GUI framework.
- **Template layer:** If using a web framework.

In order to better understand why this architecture is good for medium to
large applications, I encourage you to watch a couple of Uncle Bob Martin's
talks on this subject -- easily found on the Internet.

Anyway, good architecture is about decoupling. Now I am going to tell you
why you should decouple 1) your web framework and 2) your data persistence.


Action (or Service) layer
=========================

Do not conflate the core of your app -- the business rules -- with usage
of a web framework. You may want to switch web frameworks in the future,
or build an entirely different UI. Therefore, business rules must not
reside in controllers -- move your application's decisions to a higher layer!
Conversely, the layer that contains business rules (the Action layer)
may NOT import anything from the web framework.

http://programmers.stackexchange.com/questions/162399/how-essential-is-it-to-make-a-service-layer

Your controllers should be thin -- just get the data and call an Action.

Also do not conflate business rules with data persistence. If you keep
I/O concerns out of your Service layer, here called Action layer,
then this layer becomes truly unit-testable, which in itself is reason
enough to do this. Integrated test (meaning a test that hits a database,
even SQLite in memory) suites easily take 5+ minutes to run for large apps,
making TDD (test first) impossible. The solution is to separate decisions
in pure functions (which do no I/O) so they can be unit-tested. This way the
unit tests run instantaneously and you are able to do TDD.

MVC or MVT is missing a Service layer between the Model and the Controller.
This layer, here called Action, should contain the business rules in a pure
way, leaving UI related preoccupations to a thin controller, and storage
concerns to Models and the...


Repository layer
================

MVT, as implemented by most Python web frameworks, puts a
data persistence layer in the center of the architecture,
but Uncle Bob's Clean Architecture teaches us this is wrong.

In our solution, the model entities may remain in the center and circulate
(as data holders) through all layers -- this has always been so convenient --,
but the engine that stores and retrieves entities -- here called Repository
(in SQLAlchemy it's the session and its queries) -- must be a
dependency-injected layer.

Fowler and Robert C. Martin would have us put the SQLAlchemy models away too,
so in the future you could more easily swap SQLAlchemy with something else,
or even develop multiple storages simultaneously: SQLAlchemy, ZODB etc.,
but this piece of advice I am not following yet.

(Even so, you might be able to pull this off right now, if you remember that
you don't have to use the declarative flavor of the SQLAlchemy ORM --
you can instead declare tables, and then classes, and then mappers that
map tables to the classes.  These classes need no specific base class,
so you are free to use them as your entities.)

For now, most importantly, you are able to develop a FakeRepository
for fast unit testing of the Action layer -- or even a MemoryRepository
that stores all entities in RAM.


SQLAlchemy strategy
-------------------

SQLAlchemy creates testability challenges since it is very hard to mock out,
so the following rules must be followed:

- The session must be present in the Repository layer, which is
  dependency-injected into the Action layer.  This allows you to write
  fast unit tests for the Action layer -- by injecting a
  FakeRepository object which never touches a RDBMS.
- The session must NOT be present in the model layer (which defines entities).
  For now, I think relationships (e.g. ``User.addresses``) and
  ``object_session(self)`` can continue to exist in models normally,
  as long as you think you can implement equivalent relationships in
  the other repository strategies with the same API.
- The session must NOT be imported in the Action layer (which contains
  business rules). Really, only your Repository object can use the session.


Using Kerno
~~~~~~~~~~~

If you wish to adopt the Clean Architecture, then Kerno can help you.
Here is how.


Startup time and request time
=============================

Kerno computes some things at startup and keeps the result in a "global" object
which is an instance of the Kerno class. This instance is initialized with
the app's settings and utilities (strategies) are registered on it.
Then it is used on each request to obtain globals.
Each request consists of a call to an Action.


Component registration
======================

In order to swap components between environments, Kerno could have used the
famous and awesome
`Zope Component Architecture <http://zopecomponent.readthedocs.io/>`_,
but we are using `Reg <http://reg.readthedocs.io/>`_ instead.
Reg is very powerful and you don't need to create an interface for
each component you want to register.


Composable actions
==================

Kerno provides a base class for actions (the service layer). If you follow
the pattern, then you can create actions composed of other actions, which
might be useful to you.
