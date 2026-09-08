import fs from "node:fs";

const path = "src/StrategicBriefPanel.jsx";
let text = fs.readFileSync(path, "utf8");

function once(from, to, label) {
  const i = text.indexOf(from);
  if (i < 0) throw new Error(`missing anchor: ${label}`);
  if (text.indexOf(from, i + from.length) >= 0) throw new Error(`non-unique anchor: ${label}`);
  text = text.slice(0, i) + to + text.slice(i + from.length);
}

once(
  'import { useEffect, useMemo, useRef, useState } from "react";\n\nconst OFFICIAL_CLASS = "official_editorial";\nconst OFFICIAL_MODE = "editorial_curated";\nconst PUBLIC_STATUSES = new Set(["published", "revised"]);\n',
  'import { useEffect, useMemo, useRef, useState } from "react";\nimport { isOfficialStrategicBrief, validateStrategicBriefLibrary } from "../lib/brief/strategicPublication.js";\n',
  "validator import",
);

once(
  'function isOfficial(item) {\n  if (!item || item.publication_class !== OFFICIAL_CLASS || item.publication_mode !== OFFICIAL_MODE || !PUBLIC_STATUSES.has(item.status)) return false;\n  if (item.approval?.status !== "APPROVED") return false;\n  const q = item.qc || {};\n  return q.evidence_status === "PASS"\n    && q.red_team_status === "PASS"\n    && q.editorial_coherence_status === "PASS"\n    && q.language_terminology_status === "PASS";\n}\n\n',
  '',
  "duplicate official predicate",
);

once(
  '.then((j) => { if (alive) { setLibrary(j && Array.isArray(j.items) ? j : { items: [] }); setLoadError(false); } })',
  '.then((j) => {\n        const errors = validateStrategicBriefLibrary(j);\n        if (errors.length) throw new Error(`invalid official library: ${errors[0]}`);\n        if (alive) { setLibrary(j); setLoadError(false); }\n      })',
  "library fail-closed validation",
);

once(
  'const items = useMemo(() => (library?.items || []).filter(isOfficial).slice().sort(issueRank), [library]);',
  'const items = useMemo(() => (library?.items || []).filter(isOfficialStrategicBrief).slice().sort(issueRank), [library]);',
  "official predicate reuse",
);

fs.writeFileSync(path, text);
console.log("Strategic Brief reader now fails closed through canonical publication validator");
