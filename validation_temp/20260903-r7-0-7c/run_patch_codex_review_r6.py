#!/usr/bin/env python3
from pathlib import Path

p = Path('validation_temp/20260903-r7-0-7c/patch_codex_review_r6.py')
s = p.read_text(encoding='utf-8')
old = """        cur = obj.get('single_source_exception')
        if isinstance(cur, dict):
            obj['single_source_exception'] = {
                'allowed': True,
                'reason': 'The CNINFO / Shenzhen Stock Exchange filing is the authoritative primary document; the Sina URL is only a mirror of the same filing and is not counted as independent corroboration.',
                'mitigation': 'Visible claims are limited to figures and statements directly established by the official filing; the mirror is retained only as duplicate-document access.',
                'scope_limits': [
                    'one editorially independent owner cluster',
                    'official filing controls operative facts',
                    'document mirror does not increase independent-owner count',
                ],
            }
        else:
            obj['single_source_exception'] = True
"""
new = """        obj['single_source_exception'] = {
            'allowed': True,
            'reason': 'The CNINFO / Shenzhen Stock Exchange filing is the authoritative primary document; the Sina URL is only a mirror of the same filing and is not counted as independent corroboration.',
            'mitigation': 'Visible claims are limited to figures and statements directly established by the official filing; the mirror is retained only as duplicate-document access.',
            'scope_limits': [
                'one editorially independent owner cluster',
                'official filing controls operative facts',
                'document mirror does not increase independent-owner count',
            ],
        }
"""
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
exec(compile(s, str(p) + '[STRICT_OBJECT_SINGLE_SOURCE_EXCEPTION]', 'exec'), {'__name__': '__main__', '__file__': str(p)})
