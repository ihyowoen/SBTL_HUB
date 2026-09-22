#!/usr/bin/env python3
"""Deterministic, hash-checked PR385 migration; not imported by production."""
from pathlib import Path
import argparse, ast, hashlib

ORIGINAL = {
    'card_run_v4_binding_hardening.py': 'fd482624d3e39c24db3b23b5a53988913432370f27e9563431d56ac11136fe68',
    'stage_artifact_contract_check.py': 'b16115b0c4eb2ed8b55f19c25de94ca9ff33158347bf9b0fc3180ce60473a43d',
}

def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f'Expected exactly one migration anchor: {old[:100]!r}')
    return text.replace(old, new, 1)

def replace_node(text, name, replacement, kind='function'):
    nodes=[]
    for node in ast.parse(text).body:
        if kind == 'function' and isinstance(node, ast.FunctionDef) and node.name == name:
            nodes.append(node)
        if kind == 'constant' and isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == name for t in node.targets
        ):
            nodes.append(node)
    if len(nodes)!=1: raise ValueError(f'Expected one node {name}')
    node=nodes[0]; lines=text.splitlines(keepends=True)
    return ''.join(lines[:node.lineno-1])+replacement.rstrip()+'\n'+''.join(lines[node.end_lineno:])

def node_text(text,name):
    n=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name==name)
    return '\n'.join(text.splitlines()[n.lineno-1:n.end_lineno])+'\n'

CONTEXT = '''def _resolve_content_evidence_context(rows_by_stage, label):
    """Resolve authoritative packages once; all downstream views share them."""
    support = _upstream_evidence_token_support(rows_by_stage, label)
    packages = _nearest_upstream_evidence_packages(rows_by_stage, label, support)
    texts = {
        token: _package_texts(items[0])
        for token, items in packages.items() if items and _package_texts(items[0])
    }
    return _content_core.ResolvedEvidenceContext.from_maps(
        scope="bound_upstream", support=support, texts=texts, packages=packages,
    )
'''

GROUNDING = '''def _validate_claimed_dimension_evidence_grounding(
    density,row_06,label,true_dimensions,
    allowed_evidence_texts,allowed_evidence_packages
):
    mapping=density.get("dimension_evidence") if isinstance(density,dict) else None
    for dimension in true_dimensions:
        entry=mapping.get(dimension) if isinstance(mapping,dict) else None
        if not isinstance(entry,dict):
            continue
        fields=entry.get("fields") if isinstance(entry.get("fields"),list) else []
        refs=[ref.strip() for ref in entry.get("evidence_refs",[]) if _nonempty_text(ref)] \\
            if isinstance(entry.get("evidence_refs"),list) else []
        refs=_unique_evidence_refs_by_identity(refs,allowed_evidence_packages)
        visible_counts=Counter()
        evidence_counts=Counter()
        visible_strengths={}
        evidence_strengths={}
        for field in fields:
            text=_visible_value_text(_normalized_visible_value(field,row_06.get(field,_MISSING)))
            visible_counts.update(_signal_counter(dimension,text))
            if dimension=="changed_state":
                for key,values in _state_subject_strength_occurrences(text).items():
                    visible_strengths.setdefault(key,[]).extend(values)
        for ref in refs:
            for text in allowed_evidence_texts.get(ref,[]):
                evidence_counts.update(_signal_counter(dimension,text))
                if dimension=="changed_state":
                    for key,values in _state_subject_strength_occurrences(text).items():
                        evidence_strengths.setdefault(key,[]).extend(values)
        issues=_content_core.grounding_issues(
            dimension,visible_counts,evidence_counts,visible_strengths,evidence_strengths,
            require_realized=True,
        )
        if issues:
            raise Blocked(f"{label} {issues[0].message}")
'''

STANDALONE_GROUNDING = '''                    visible_subject_strengths = {}
                    evidence_subject_strengths = {}
                    if name == "changed_state":
                        for field in fields:
                            text = _visible_value_text(_normalized_visible_value(field, item.get(field)))
                            for key, strengths in _content_binding._state_subject_strength_occurrences(text).items():
                                visible_subject_strengths.setdefault(key, []).extend(strengths)
                        for ref in unique_refs:
                            for text in evidence_texts.get(ref, []):
                                for key, strengths in _content_binding._state_subject_strength_occurrences(text).items():
                                    evidence_subject_strengths.setdefault(key, []).extend(strengths)
                    findings.extend(issue.as_finding(scope) for issue in _content_core.grounding_issues(
                        name, visible_counts, evidence_counts,
                        visible_subject_strengths, evidence_subject_strengths,
                        require_realized=False,
                    ))
'''


def phase_a(root):
    paths={name:root/'validation_scripts'/name for name in ORIGINAL}
    data={name:path.read_text(encoding='utf-8') for name,path in paths.items()}
    for name,path in paths.items():
        if hashlib.sha256(path.read_bytes()).hexdigest()!=ORIGINAL[name]:
            raise ValueError('Migration source hash mismatch: '+name)
    b=data['card_run_v4_binding_hardening.py']; s=data['stage_artifact_contract_check.py']
    b=replace_once(b,'ROOT = Path(__file__).resolve().parents[1]\n',
        'ROOT = Path(__file__).resolve().parents[1]\n'
        'if str(ROOT) not in sys.path:\n    sys.path.insert(0, str(ROOT))\n'
        'from validation_scripts import content_enrichment_core as _content_core\n')
    s=replace_once(s,'from validation_scripts import card_run_v4_binding_hardening as _content_binding\n',
        'from validation_scripts import card_run_v4_binding_hardening as _content_binding\n'
        'from validation_scripts import content_enrichment_core as _content_core\n')
    for name in ('VISIBLE_COPY_FIELDS','DENSITY_DIMENSIONS','CONTENT_BASELINE_STRATEGY','PRESENTATION_HTML_TAG_RE'):
        b=replace_node(b,name,f'{name} = _content_core.{name}',kind='constant')
        s=replace_node(s,name,f'{name} = _content_core.{name}',kind='constant')
    for name in ('_strip_paired_presentation_markup','_normalize_text','_normalized_visible_value','_visible_value_text'):
        b=replace_node(b,name,f'{name} = _content_core.{name}')
        s=replace_node(s,name,f'{name} = _content_core.{name}')
    b=replace_node(b,'_strength_multiset_covers','_strength_multiset_covers = _content_core._strength_multiset_covers')
    b=replace_node(b,'_validate_claimed_dimension_evidence_grounding',GROUNDING)
    density=node_text(b,'_validate_density_audit')
    start=density.index('    density=audit.get('); end=density.index('    _validate_dimension_evidence(')
    density=density[:start]+'''    density=audit.get("density_audit") if isinstance(audit,dict) else None
    issues=_content_core.density_policy_issues(density,no_change=no_change)
    if issues:
        raise Blocked(f"{label} {issues[0].message}")
    true_dimensions=[name for name in DENSITY_DIMENSIONS if density["dimensions"][name]]

'''+density[end:]
    b=replace_node(b,'_validate_density_audit',density)
    b=replace_once(b,'def validate_content_enrichment_delta(',CONTEXT+'\n\ndef validate_content_enrichment_delta(')
    b=replace_once(b,'''    allowed_evidence_support=_upstream_evidence_token_support(rows_by_stage,label)
    allowed_evidence_texts=_upstream_evidence_token_texts(
        rows_by_stage,label,allowed_evidence_support
    )
    allowed_evidence_packages=_upstream_evidence_token_packages(
        rows_by_stage,label,allowed_evidence_support
    )
''','''    evidence_context=_resolve_content_evidence_context(rows_by_stage,label)
    allowed_evidence_support,allowed_evidence_texts,allowed_evidence_packages=evidence_context.legacy_maps()
''')
    # Keep source-scope resolution at each existing trust boundary in A; only
    # detach it once so shared policy cannot mutate or recombine its evidence.
    s=replace_once(s,'''    evidence_support = _row_evidence_token_support(item)
    evidence_texts = _content_binding._row_evidence_token_texts(item)
    evidence_packages = _content_binding._row_evidence_token_packages(item)
''','''    evidence_context = _content_core.ResolvedEvidenceContext.from_maps(
        scope="local_row", support=_row_evidence_token_support(item),
        texts=_content_binding._row_evidence_token_texts(item),
        packages=_content_binding._row_evidence_token_packages(item),
    )
    evidence_support, evidence_texts, evidence_packages = evidence_context.legacy_maps()
''')
    function=node_text(s,'_dimension_evidence_findings')
    start=function.index('                    missing_signals = {')
    end=function.index('    return findings\n', start)
    function=function[:start]+STANDALONE_GROUNDING+function[end:]
    s=replace_node(s,'_dimension_evidence_findings',function)
    function=node_text(s,'_content_enrichment_audit_findings')
    start=function.index('    if density.get("status") != "PASS":')
    end=function.index('    if changed_valid and not changed and no_change is True:',start)
    function=function[:start]+'''    findings.extend(issue.as_finding(scope) for issue in _content_core.density_policy_issues(
        density, no_change=changed_valid and not changed and no_change is True,
    ))
    dimensions = density.get("dimensions")
    valid_dimensions = (
        isinstance(dimensions, dict) and set(dimensions) == set(DENSITY_DIMENSIONS)
        and all(isinstance(dimensions[name], bool) for name in DENSITY_DIMENSIONS)
    )
    true_dimensions = [name for name in DENSITY_DIMENSIONS if dimensions[name]] if valid_dimensions else []

'''+function[end:]
    start=function.index('            if len(true_dimensions) < 4:')
    end=function.index('            findings.extend(_dimension_evidence_findings',start)
    function=function[:start]+function[end:]
    start=function.index('        if not true_dimensions:')
    end=function.index('            findings.extend(_dimension_evidence_findings',start)
    function=function[:start]+'        if true_dimensions:\n'+function[end:]
    s=replace_node(s,'_content_enrichment_audit_findings',function)
    for name,text in [('card_run_v4_binding_hardening.py',b),('stage_artifact_contract_check.py',s)]:
        ast.parse(text)
        paths[name].write_text(text,encoding='utf-8')


def phase_b(root):
    p=root/'validation_scripts/card_run_v4_binding_hardening.py'; b=p.read_text()
    b=replace_once(b,'''    allowed_evidence_texts,allowed_evidence_packages
):
    mapping=density.get("dimension_evidence") if isinstance(density,dict) else None''',
        '''    allowed_evidence_texts,allowed_evidence_packages,*,no_change
):
    mapping=density.get("dimension_evidence") if isinstance(density,dict) else None''')
    b=replace_once(b,'            require_realized=True,','            require_realized=no_change,')
    b=replace_once(b,'''        allowed_evidence_texts,allowed_evidence_packages,
    )
    if not actual_changed:
''','''        allowed_evidence_texts,allowed_evidence_packages,no_change=not actual_changed,
    )
    if not actual_changed:
''')
    # Remove the redundant second implementation; shared grounding already
    # requires an evidence-grounded realized occurrence for no-change only.
    b=replace_once(b,'''    if not actual_changed:
        _validate_zero_delta_realized_state(
            audit["density_audit"],row_06,label,allowed_evidence_packages
        )
''','')
    b=replace_node(b,'_validate_zero_delta_realized_state','')
    ast.parse(b); p.write_text(b)
    p=root/'validation_scripts/stage_artifact_contract_check.py';s=p.read_text()
    s=replace_once(s,'                        require_realized=False,',
        '''                        require_realized=(
                            item.get("content_enrichment_audit", {}).get("no_change_required") is True
                        ),''')
    s=replace_once(s,'    print(json.dumps(result, ensure_ascii=False, indent=2))',
        '''    if args.stage == "0.6":
        result["validation_scope"] = {
            "mode": "stage_artifact_only",
            "not_verified": ["upstream_evidence_authority", "actual_visible_copy_delta", "materialized_operation"],
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))''')
    ast.parse(s);p.write_text(s)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['a','b']);p.add_argument('repo',type=Path)
    a=p.parse_args();(phase_a if a.phase=='a' else phase_b)(a.repo)
