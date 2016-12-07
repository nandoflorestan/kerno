from .state import Peto


class Operation:
    """A named series of actions (steps) to be executed."""

    def __init__(self, title, actions=None):
        """Constructor."""
        self.title = title
        self.actions = list(actions)
        assert self.actions, 'Empty operations are not allowed.'

    def __call__(self, kerno, user, payload):
        """Execute actions of this instance as ``user`` with ``payload``."""
        peto = Peto(kerno=kerno, user=user, operation=self, payload=payload)
        for cls in self.actions:
            action = cls(peto)
            action()
        return peto.rezulto
