#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import base64, collections, gzip, hashlib, json, re

RUN_TAG = "20260707_134245"
ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "public/data/cards.json"
PAYLOAD_GLOB = "prompt08_20260707_134245_payload_part*.b64"
WORKFLOW_PATH = ROOT / ".github/workflows/apply-prompt08-20260707_134245.yml"
SCRIPT_PATH = ROOT / "scripts/apply_prompt08_20260707_134245.py"

def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()

def canonical_url(url: str) -> str:
    p=urlsplit(url.strip())
    host=p.netloc.lower()
    if host.startswith("www."): host=host[4:]
    path=re.sub(r"/+$","",p.path) or "/"
    query=[(k,v) for k,v in parse_qsl(p.query,keep_blank_values=True)
           if not k.lower().startswith("utm_") and k.lower() not in {"fbclid","gclid","outputtype"}]
    return urlunsplit((p.scheme.lower(),host,path,urlencode(query),""))

payload_parts=sorted((ROOT / "tmp").glob(PAYLOAD_GLOB))
assert payload_parts
payload_b64="".join(p.read_text().strip() for p in payload_parts)
payload=json.loads(gzip.decompress(base64.b64decode(payload_b64)).decode("utf-8"))
baseline_bytes=DATA_PATH.read_bytes()
assert git_blob_sha(baseline_bytes)==payload["expected_baseline_git_blob_sha"]
baseline=json.loads(baseline_bytes)
assert baseline["total"]==payload["expected_baseline_count"]==len(baseline["cards"])

existing_ids={c["id"] for c in baseline["cards"]}
existing_specs={c.get("source_spec_id") for c in baseline["cards"] if c.get("source_spec_id")}
exact=collections.defaultdict(set)
canon=collections.defaultdict(set)
for c in baseline["cards"]:
    for u in c.get("urls",[]) or []:
        exact[u].add(c["id"])
        canon[canonical_url(u)].add(c["id"])

new_cards=payload["new_cards"]
assert len(new_cards)==13
for c in new_cards:
    assert c["id"] not in existing_ids
    assert c["source_spec_id"] not in existing_specs
    assert c["github_ready"] is True and c["pr_candidate_ready"] is True
    for u in c.get("urls",[]) or []:
        assert not exact.get(u)
        assert not canon.get(canonical_url(u))

all_cards=baseline["cards"]+new_cards
assert len({c["id"] for c in all_cards})==len(all_cards)==payload["expected_final_count"]
all_cards.sort(key=lambda c:(c["date"],c["id"]),reverse=True)
baseline["updated"]=payload["updated"]
baseline["total"]=payload["expected_final_count"]
baseline["cards"]=all_cards
baseline["merge_metadata"]=payload["merge_metadata"]
DATA_PATH.write_text(json.dumps(baseline,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
out=DATA_PATH.read_bytes()
assert hashlib.sha256(out).hexdigest()==payload["expected_candidate_sha256"]

# Remove temporary automation files so the final PR diff contains only cards.json.
for path in [*payload_parts,SCRIPT_PATH,WORKFLOW_PATH]:
    if path.exists():
        path.unlink()
print("Prompt 0.8 merge applied:", len(new_cards), "cards; final", len(all_cards))
# trigger: workflow-present push
