# Audit checkpoint 18 — formal 0.1P delta and corrected CP17 source identity

Date: 2026-11-01. Branch-only evidence; no changes to `main`, `Full`, `Related`, production, or published stories.

## Drive evidence

- [CP18 report](https://drive.google.com/file/d/1j7ft0dIy9wrv_Hyuj8dHlaheLUEjxbCQ/view)
- [CP18 native formal JSON, original-source adjudications, validators, corrected CP17 worksheet and reproducible scripts — ZIP](https://drive.google.com/file/d/1imqNfoALGrYFa1TifCoDyFHE68tB25ha/view)
- [CP18 independent 27-check QC](https://drive.google.com/file/d/1CeT-nH_7byL8or75bdbaPD64RULviMhL/view)
- [CP17 corrected triage JSON, superseding original CP17 triage](https://drive.google.com/file/d/1OuLaUjb-4xoJGUyjvZg7JUSlK7u33yvh/view)
- [CP18 receipt](https://drive.google.com/file/d/1V1BcaHYzaRPcZxgIeXESUlIvnhFDj_6u/view)

## Evidence hashes

| Artifact | SHA256 |
| --- | --- |
| CP18 ZIP | `1baf0c1fd653d9419068364e68be5c0f5f3b181ea6d22bdcdb73af0ba7869980` |
| CP18 native JSON | `4b9039f9f045e92ae5485ddab4ab0ab40bb19da8fdf59bb02c6c0b5adba44b66` |
| CP18 report | `bb86680dc13ed4f4b9f008780471b4df764d2ceaf7f4b66313665fe937b98e25` |
| CP18 independent QC | `f6a19ff27b8bb24acf74224022391ace90d1b5973b2fb270d5f103422ef8f455` |
| Corrected CP17 triage | `3384589e886c79fdd07e34c258583b498928ae1fad9e151827f5653713692b38` |
| Original locked CP16 | `d36893b263dfed269388d40680a7896ebee0b68127619cded66baeb951084fef` |
| Original Full 1,676 cards | `d22f0d4e39e035b9537b3e9abdf48abe6b7eb80f7e477e87aff1284f9e27e0d9` |

## Formal status and safety

- Original 1,330 Source IDs preserved. Formal decisions 99 → **105**; pending 1,231 → **1,225**; strict selectors 18 → **20**.
- New strict events: SK On/L&F September17 contracted LFP cathode supply; Korean September22 end-of-life vehicle drive-motor rare-earth magnet collection pilot MOU.
- Three supporting Source IDs and one KPX preannounced registration procedural WATCH resolved. Original 54 previously reviewed Source IDs now all formal.
- CP17 safe article review units corrected **1,129 → 1,130** because two DAPA documents shared `bbsSeq` but had different `docSeq`. This is a source-review count, *not* an economic-event count.
- Two native validators **PASS**; independent CP18 QC **PASS 27/27**; corrected CP17 QC **PASS 21/21**.
- Stage A globally **HOLD** until the outstanding 1,225 Source IDs are formally disposed and relevant native checks are re-run. **No Stage B access or canonical card write.**

The ZIP contains the complete 63MB JSON in compressed form and all reconstruct/verify scripts. This GitHub directory keeps text evidence, QC and reproducible code for a separate audit trail.
