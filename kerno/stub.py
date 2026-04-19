"""Utility for creating verified test doubles to avoid contract drift."""

import inspect
from typing import Any, Callable, Dict, Self, Type, TypeVar
from unittest.mock import Mock

T = TypeVar("T", bound=Type[Any])


class VerifyingDouble:
    """A test double that verifies its stubs against a real class's signatures.

    Example:

    ```python
    class RealRepo:
        def get_user(self, user_id: int, active_only: bool = True): ...

    stub = VerifyingDouble(RealRepo)
    # Valid: matches required arguments, ignores optional ones.
    stub.arm("get_user", lambda user_id: {"id": user_id})
    # Raises TypeError: 'tenant_id' does not exist in RealRepo.get_user
    # stub.arm("get_user", lambda user_id, tenant_id: ...)
    ```
    """

    def __init__(self, real_class: T) -> None:
        self._real_class: T = real_class

    def arm(self, method_name: str, implementation: Callable) -> Self:
        """Verify the implementation signature and attach it as a method."""
        real_method = getattr(self._real_class, method_name, None)
        if not real_method or not (
            inspect.isfunction(real_method) or inspect.ismethod(real_method)
        ):
            raise AttributeError(
                f"'{method_name}' not found as a method in {self._real_class.__name__}"
            )
        if not isinstance(implementation, Mock):
            self.verify_subset(
                method_name, real_method, implementation, self._real_class.__name__
            )
        setattr(self, method_name, implementation)
        return self

    def _required_params(self, real_params):
        return [
            p
            for p, v in real_params.items()
            if v.default is inspect.Parameter.empty and p != "self"
        ]

    def verify_subset(
        self,
        name: str,
        real_method: Callable,
        implementation: Callable,
        class_name: str,
    ) -> None:
        """Check existence of arguments and presence of all required arguments.

        - Ensure all stub arguments exist in real signature.
        - Ensure all required arguments from real signature exist as stub arguments.
        """
        real_sig = inspect.signature(real_method)
        stub_sig = inspect.signature(implementation)
        real_params = real_sig.parameters
        stub_params = stub_sig.parameters
        for param_name in stub_params:
            if param_name not in real_params and param_name != "self":
                required = self._required_params(real_params)
                raise TypeError(
                    f"Stub for '{name}' uses unknown argument '{param_name}'. "
                    f"Required arguments are: {', '.join(required)}"
                )
        for param_name, param in real_params.items():
            if param_name == "self":
                continue
            is_required = (
                param.default is inspect.Parameter.empty
                and param.kind
                not in (
                    param.VAR_POSITIONAL,
                    param.VAR_KEYWORD,
                )
            )
            if is_required and param_name not in stub_params:
                required = self._required_params(real_params)
                raise TypeError(
                    f"Stub for '{name}' is missing required argument '{param_name}' from {class_name}. "
                    f"Required arguments are: {', '.join(required)}"
                )
