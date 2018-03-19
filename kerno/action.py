"""An abstract base for class-based actions."""

from abc import ABCMeta, abstractmethod
from .kerno import Kerno
from .state import Rezulto

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from typing import Dict  # noqa


class Action(metaclass=ABCMeta):
    """Abstract base for class-based actions."""

    def __init__(self, kerno: Kerno, user: Any, repo: Any) -> None:
        """Construct."""
        self.kerno = kerno
        self.user = user
        self.repo = repo

    @abstractmethod
    def __call__(self, **kw) -> Rezulto:
        """Must be overridden and, if happy, return a Rezulto instance."""
