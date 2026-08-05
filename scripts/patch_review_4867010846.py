#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

TARGET = Path("validation_scripts/stage_lineage_contract_check.py")

OLD = '''def _independent_clause_for_conditional_or_concessive(text):
    """Return the independent clause without binding across a dependent marker."""
    marker = _base_layer._base.re.search(
        _CONDITIONAL_OR_CONCESSIVE_PATTERN, text
    )
    if marker is None:
        return text

    prefix = text[:marker.start()].strip(" ,;")
    if prefix:
        # A trailing dependent condition/concession cannot supply the
        # interpretation object for an effect in the independent prefix.
        return prefix

    # With a leading dependent condition/concession, the independent clause
    # follows its comma/semicolon boundary. Fail closed when no such boundary
    # is present instead of guessing where the main clause begins.
    dependent_tail = text[marker.end():].lstrip()
    clause_parts = _base_layer._base.re.split(
        r"[,;]\\s*", dependent_tail, maxsplit=1
    )
    if len(clause_parts) != 2:
        return ""
    return clause_parts[1].strip()
'''

NEW = '''def _independent_clause_for_conditional_or_concessive(text):
    """Keep the main clause while removing dependent conditions/concessions."""
    current = text.strip()

    # Re-evaluate after every extraction. This matters when a leading
    # concession is followed by a main clause that itself carries a trailing
    # condition, and when a comma-delimited medial concession interrupts the
    # subject/predicate of the same main clause.
    for _ in range(16):
        marker = _base_layer._base.re.search(
            _CONDITIONAL_OR_CONCESSIVE_PATTERN, current
        )
        if marker is None:
            return current.strip()

        raw_prefix = current[:marker.start()]
        prefix = raw_prefix.strip(" ,;")

        if not prefix:
            # A leading dependent clause must end at a comma/semicolon. Keep
            # the following main clause, then inspect it again for any later
            # dependent marker instead of accepting it wholesale.
            separator = _base_layer._base.re.search(
                r"[,;]\\s*", current[marker.end():]
            )
            if separator is None:
                return ""
            current = current[marker.end() + separator.end():].strip()
            continue

        if raw_prefix.rstrip().endswith((",", ";")):
            # A medial comma/semicolon-delimited concession is parenthetical,
            # not the end of the independent clause. Remove only that
            # dependent segment and reconnect the surrounding main clause.
            remainder = current[marker.end():]
            separator = _base_layer._base.re.search(r"[,;]\\s*", remainder)
            if separator is None:
                return prefix
            suffix = remainder[separator.end():].strip()
            current = " ".join(part for part in (prefix, suffix) if part)
            continue

        # A trailing dependent condition/concession cannot supply the
        # interpretation object for an effect in the independent prefix.
        current = prefix

    # Malformed or adversarial nesting must fail closed rather than loop or
    # guess at a main clause.
    return ""
'''

text = TARGET.read_text(encoding="utf-8")
if text.count(OLD) != 1:
    raise SystemExit(f"expected exactly one target block, found {text.count(OLD)}")
TARGET.write_text(text.replace(OLD, NEW), encoding="utf-8")
print(f"patched {TARGET}")
