from types import FunctionType
import reg
from .action import Action
from .state import Peto


class Operation:
    """A named series of actions (steps) to be executed."""

    def __init__(self, name, actions):
        """Constructor."""
        assert actions, 'Empty operations are not allowed.'
        self.name = name
        self.actions = tuple(actions)

    def __call__(self, kerno, user, payload, peto_vars):
        """Execute the actions of this instance as ``user`` with ``payload``.

        Actions can be:

        - A function that receives an argument ``peto``.
        - A class having both a constructor that receives an argument ``peto``,
          and a __call__() method.
        """
        peto = Peto(kerno=kerno, user=user, operation=self, payload=payload)
        for key, val in peto_vars.items():
            setattr(peto, key, val)
        for action in self.actions:
            if issubclass(action, Action):
                action_instance = action(peto)
                action_instance()
            elif isinstance(action, FunctionType):
                action(peto)
            else:
                raise RuntimeError(
                    '{} is not a function or an Action subclass!'
                    .format(action))
        return peto  # which has .rezulto


class OperationRegistry:
    """Mixin that contains Kerno's operation registry."""

    def __init__(self):
        """Constructor section."""
        # The registry must be local to each Kerno instance, not static.
        # This is why we define the registry inside the constructor:
        @reg.dispatch(reg.match_key('name', lambda name: name))
        def get_operation(name):
            """Return a operation class, or None, according to configuration."""
            raise ValueError('Unknown operation: "{}"'.format(name))
        self.get_operation = get_operation

    def register_operation(self, name, actions=None):
        """Register an Operation under ``name`` at startup for later use."""
        # print('Registering operation ', name)
        if isinstance(name, Operation) and actions is None:
            operation = name
        elif actions is not None and name and isinstance(name, str):
            operation = Operation(name=name, actions=actions)
        else:
            raise RuntimeError('register_operation() called with wrong args!')
        self.get_operation.register(lambda name: operation, name=name)

    def run_operation(self, operation, user, payload, **kw):
        """Execute, as ``user``, the specified operation with ``payload``."""
        if isinstance(operation, str):
            operation = self.get_operation(operation)
        return operation(kerno=self, user=user, payload=payload, peto_vars=kw)
