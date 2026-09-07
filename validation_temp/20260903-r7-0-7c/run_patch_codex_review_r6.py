#!/usr/bin/env python3
from pathlib import Path

p = Path('validation_temp/20260903-r7-0-7c/patch_codex_review_r6.py')
s = p.read_text(encoding='utf-8')
old = "assert s['single_source_exception']['allowed'] is True"
new = "assert s['single_source_exception'] is True or (isinstance(s['single_source_exception'], dict) and s['single_source_exception'].get('allowed') is True)"
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
exec(compile(s, str(p) + '[SCHEMA_COMPAT_SINGLE_SOURCE_EXCEPTION]', 'exec'), {'__name__': '__main__', '__file__': str(p)})
