#!/usr/bin/env python3
"""Canonical V3 loader with trimmed evidence/confirmation constraints."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_BASE_PATH = Path(__file__).with_name("v3_contract_review4871719239_base.py")
_SPEC = importlib.util.spec_from_file_location(
    "validation_scripts.v3_contract_review4871719239_base",
    _BASE_PATH,
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot load canonical V3 contract base from {_BASE_PATH}")
_base = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_base)

for _name in dir(_base):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_base, _name)


def _expected_structured_text_definition(key_pairs):
    """Build exact schemas with minimum lengths applied after trimming."""
    structured_pattern = r"^\s*\S[\s\S]*\S\s*$"
    free_text_pattern = r"^\s*\S[\s\S]{2,}\S\s*$"
    options = []
    for first_key, second_key in key_pairs:
        options.append(
            {
                "type": "object",
                "required": [first_key, second_key],
                "properties": {
                    first_key: {
                        "type": "string",
                        "minLength": 2,
                        "pattern": structured_pattern,
                    },
                    second_key: {
                        "type": "string",
                        "minLength": 2,
                        "pattern": structured_pattern,
                    },
                },
                "additionalProperties": True,
            }
        )
    options.append(
        {"type": "string", "minLength": 4, "pattern": free_text_pattern}
    )
    return {"oneOf": options}


# The base validator resolves this helper through its module globals.
_base._expected_structured_text_definition = _expected_structured_text_definition
globals()["_expected_structured_text_definition"] = (
    _expected_structured_text_definition
)

load_contract = _base.load_contract
validate_contract_document = _base.validate_contract_document
contract_projection = _base.contract_projection
