"""Repositories are persistence strategies.

The repository pattern describes a storage component that can be easily
swapped through dependency injection.

The purpose of a repository is:

1. To allow you to easily swap data access technology
2. To give a name to each query so the code becomes easier to read
2. To isolate data access code
3. Such that you can easily write unit tests (not integration tests) for the
   action / business layer. Because it is much, much easier to fake a
   repository than it is to fake SQLAlchemy and other ORMs.

Extracting a repository from existing code does reveal repeated queries -- and
repetition is the root of all evil in software creation.

I recommend against building generic repositories. See
http://ben-morris.com/why-the-generic-repository-is-just-a-lazy-anti-pattern
"""
