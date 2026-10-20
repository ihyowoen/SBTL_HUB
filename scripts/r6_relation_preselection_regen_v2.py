from pathlib import Path

p=Path('scripts/r6_relation_preselection_regen.py')
s=p.read_text()
old="feats={k:sorted({v for x in srcrows for v in x.get('matched_features',{}).get(k,[])}) for k in feature_keys}; score=max(int(x.get('routing_hint_score',0)) for x in srcrows)"
new="feats={k:sorted({v for x in srcrows for v in x.get('matched_features',{}).get(k,[])}) for k in feature_keys}; numeric_scores=[x.get('routing_hint_score') for x in srcrows if isinstance(x.get('routing_hint_score'),(int,float))]; score=max(numeric_scores) if numeric_scores else None"
assert old in s, 'expected R6 null-score expression not found'
patched=s.replace(old,new,1)
exec(compile(patched,str(p), 'exec'))
