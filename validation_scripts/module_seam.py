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


def clone_module_with_rebound_functions(
    source: ModuleType,
    *,
    module_name: str,
    function_names: tuple[str, ...],
) -> ModuleType:
    """Clone a module and rebind selected inherited functions to the clone.

    ``clone_module_with_shared_globals`` automatically rebinds functions owned
    by ``source``. Compatibility layers can also export functions inherited from
    a nested module. The explicitly named functions are cloned again so they all
    resolve through the new module's one shared globals dictionary.
    """
    cloned = clone_module_with_shared_globals(
        source,
        module_name=module_name,
    )
    namespace = cloned.__dict__

    for name in function_names:
        function = getattr(source, name, None)
        if not isinstance(function, FunctionType):
            raise TypeError(
                f"module function {name!r} is not a Python function on {source.__name__}"
            )
        namespace[name] = _clone_function_into_namespace(
            function,
            namespace,
            module_name=module_name,
        )

    return cloned


def clone_module_with_cloned_dependency(
    source: ModuleType,
    *,
    dependency_name: str,
    module_name: str,
    dependency_source: ModuleType | None = None,
) -> ModuleType:
    """Clone a policy layer and reconstruct its nested dependency ownership.

    ``dependency`` is the layer's current nested module and is used to identify
    exports inherited by identity. ``dependency_source`` is the clean module
    used to build the new nested namespace. When omitted, a module-valued
    ``source._core`` is preferred; otherwise the current dependency is cloned.

    This distinction recreates historical file-execution order: a clean core is
    cloned first, the layer captures any ``_prior_<name>`` aliases from it, and
    layer-owned overrides are then installed into the nested core. No module file
    is executed a second time and canonical imported modules remain untouched.
    """
    dependency = getattr(source, dependency_name, None)
    if not isinstance(dependency, ModuleType):
        raise TypeError(
            f"module dependency {dependency_name!r} is not a module on {source.__name__}"
        )

    if dependency_source is None:
        clean_candidate = getattr(source, "_core", None)
        dependency_source = (
            clean_candidate if isinstance(clean_candidate, ModuleType) else dependency
        )
    if not isinstance(dependency_source, ModuleType):
        raise TypeError("dependency_source must be a module")

    cloned = clone_module_with_shared_globals(
        source,
        module_name=module_name,
    )
    dependency_module_name = (
        f"{module_name}.{dependency_name.lstrip('_') or 'dependency'}"
    )
    cloned_dependency = clone_module_with_shared_globals(
        dependency_source,
        module_name=dependency_module_name,
    )
    clean_dependency_exports = dict(vars(cloned_dependency))
    setattr(cloned, dependency_name, cloned_dependency)

    dependency_values = list(vars(dependency).items())
    layer_owned_dependency_overrides: list[tuple[str, Any]] = []

    for name, value in vars(source).items():
        replacement = None
        source_owned_function = (
            isinstance(value, FunctionType)
            and value.__globals__ is source.__dict__
        )

        if value is dependency_source:
            replacement = cloned_dependency
        elif name.startswith("_prior_"):
            dependency_export = name.removeprefix("_prior_")
            if dependency_export in clean_dependency_exports:
                replacement = clean_dependency_exports[dependency_export]
        elif source_owned_function:
            if name in vars(dependency) and vars(dependency)[name] is value:
                layer_owned_dependency_overrides.append(
                    (name, getattr(cloned, name))
                )
        elif name in vars(dependency) and value is vars(dependency)[name]:
            replacement = clean_dependency_exports.get(name)
        elif isinstance(value, (FunctionType, *_MUTABLE_GLOBAL_TYPES)):
            for dependency_export, dependency_value in dependency_values:
                if value is dependency_value:
                    replacement = clean_dependency_exports.get(dependency_export)
                    break

        if replacement is not None:
            setattr(cloned, name, replacement)

    for name, replacement in layer_owned_dependency_overrides:
        setattr(cloned_dependency, name, replacement)

    return cloned
