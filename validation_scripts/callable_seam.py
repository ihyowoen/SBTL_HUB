#!/usr/bin/env python3
"""Utilities for isolating compatibility-layer callable globals."""
from __future__ import annotations

from types import FunctionType
from typing import Any, Callable, Mapping


def clone_function_with_globals(
    function: Callable[..., Any],
    global_overrides: Mapping[str, Any],
    *,
    module_name: str,
) -> Callable[..., Any]:
    """Clone a Python function with an isolated globals mapping.

    Compatibility layers historically reused one function object and mutated
    its ``__globals__`` in place. A clone prevents later imports from changing
    the policy seen by an already-imported stable or public entrypoint.
    """
    namespace = dict(function.__globals__)
    namespace.update(global_overrides)
    cloned = FunctionType(
        function.__code__,
        namespace,
        name=function.__name__,
        argdefs=function.__defaults__,
        closure=function.__closure__,
    )
    cloned.__kwdefaults__ = function.__kwdefaults__
    cloned.__annotations__ = dict(getattr(function, "__annotations__", {}))
    cloned.__dict__.update(getattr(function, "__dict__", {}))
    cloned.__doc__ = function.__doc__
    cloned.__module__ = module_name
    cloned.__qualname__ = function.__qualname__
    return cloned
