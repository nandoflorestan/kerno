"""This module contains a base class for SQLAlchemy-based repositories.

The repository pattern describes a storage component that can be easily
swapped through dependency injection.
"""


class BaseSQLAlchemyRepository:
    """Base class for a SQLAlchemy-based repository."""

    def __init__(self, mundi, session_factory):
        """Construct a SQLAlchemy repository instance to serve ONE request.

        - ``mundi`` is the Mundi instance for the current application.
        - ``session_factory`` is a function that returns a
          SQLAlchemy session to be used in this request -- scoped or not.
        """
        self.mundi = mundi
        self.sas = self.get_sas(session_factory)

    def get_sas(self, session_factory):
        """Obtain a new SQLAlchemy session instance."""
        is_scoped_session = hasattr(session_factory, 'query')
        # Because we don't want to depend on SQLAlchemy:
        if callable(session_factory) and not is_scoped_session:
            return session_factory()
        else:
            return session_factory
