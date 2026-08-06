#!/usr/bin/env python3
"""Utilities for cloning module-owned callables into an isolated namespace."""
from __future__ import annotations

from collections.abc import MutableMapping, MutableSequence, MutableSet
from copy import deepcopy
from types import FunctionType, ModuleType
from typing import Any

_MUTABLE_GLOBAL_TYPES = (MutableMapping, MutableSequence, MutableSet)


def _clone_namespace_value(
    name: str,
    value: Any,
    memo: dict[int, Any],
) -> Any:
    """Copy mutable policy globals while retaining shared runtime primitives."""
    if name == "__builtins__" or not isinstance(value, _MUTABLE_GLOBAL_TYPES):
        return value
    try:
        return deepcopy(value, memo)
    except Exception as exc:  # pragma: no cover - defensive fail-closed path
        raise TypeError(f"cannot isolate mutable module global {name!r}") from exc


def _clone_function_into_namespace(
    function: FunctionType,
    namespace: dict[str, Any],
    *,
    module_name: str,
) -> FunctionType:
    """Clone one function so it resolves globals from ``namespace``."""
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


def clone_module_with_shared_globals(
    source: ModuleType,
    *,
    module_name: str,
) -> ModuleType:
    """Clone a module namespace without loading its file a second time.

    Functions defined by ``source`` are rebound to one shared cloned globals
    dictionary. Mutable policy containers are deep-copied with one shared memo,
    preserving aliases inside the clone while preventing source-state leakage.
    The canonical imported module stays untouched.
    """
    cloned = ModuleType(module_name, source.__doc__)
    namespace = cloned.__dict__
    mutable_copy_memo: dict[int, Any] = {}

    for name, value in vars(source).items():
        if name in {"__name__", "__package__", "__loader__", "__spec__"}:
            continue
        namespace[name] = _clone_namespace_value(
            name,
            value,
            mutable_copy_memo,
        )

    namespace["__name__"] = module_name
    namespace["__package__"] = module_name.rpartition(".")[0]

    for name, value in list(vars(source).items()):
        if isinstance(value, FunctionType) and value.__globals__ is source.__dict__:
            namespace[name] = _clone_function_into_namespace(
                value,
                namespace,
                module_name=module_name,
            )

    return cloned
