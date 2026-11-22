"""MaStR 2026-10-01 exact catalog country-code audit; no population estimate."""
import json
from pathlib import Path
import zipfile
from lxml import etree
from G5_14_R16_MASTR_RANGE_VERIFY_20261119 import HttpRangeFile
URL="https://download.marktstammdatenregister.de/Stichtag/Gesamtdatenexport_20261001_26.1.zip"
out=Path("g514_output")
out.mkdir(exist_ok=True)
r={}
remote=HttpRangeFile(URL)
with zipfile.ZipFile(remote) as z:
    for kind,element_tag in (("Katalogwerte.xml","Katalogwert"),("Katalogkategorien.xml","KatalogKategorie")):
        info=next((x for x in z.infolist() if x.filename.lower()==kind.lower()),None)
        if info is None:
            r[kind]={"status":"MISSING"};continue
        cases=[]
        with z.open(info) as src:
            for _,el in etree.iterparse(src,events=("end",),tag=element_tag,huge_tree=True,resolve_entities=False,no_network=True):
                d={c.tag.rsplit("}",1)[-1]:" ".join(c.itertext()).strip() for c in el}
                if kind=="Katalogwerte.xml":
                    if d.get("Wert","").casefold() in ("deutschland","batterie","in betrieb"):
                        cases.append(d)
                elif d.get("Id") in ("6","102") or any("Land" in v or "Staat" in v for v in d.values()):
                    cases.append(d)
                el.clear()
                while el.getprevious() is not None: del el.getparent()[0]
        r[kind]={"cases":cases,"crc":f"{info.CRC:08x}"}
    sample_info=next(x for x in z.infolist() if x.filename.startswith("EinheitenStromSpeicher") and x.filename.endswith(".xml"))
    with z.open(sample_info) as src:
        raw_samples=[]
        for _,e in etree.iterparse(src,events=("end",),tag="EinheitStromSpeicher",huge_tree=True,resolve_entities=False,no_network=True):
            raw={c.tag.rsplit("}",1)[-1]:" ".join(c.itertext()).strip() for c in e}
            raw_samples.append({k:raw.get(k,"") for k in ("EinheitMastrNummer","SpeMaStRNummer","Land","EinheitBetriebsstatus","Technologie","Bruttoleistung","Inbetriebnahmedatum")})
            e.clear()
            while e.getprevious() is not None: del e.getparent()[0]
            if len(raw_samples)==50:break
    r["sample"]={"file":sample_info.filename,"records":raw_samples}
print("ORIGINAL_OFFICIAL_CATALOG",json.dumps({k:(v.get("cases",v) if k!="sample" else {"file":v["file"],"records":v["records"][:8]}) for k,v in r.items()},ensure_ascii=False))
(out/"official_catalog_country_probe.json").write_text(json.dumps(r,indent=2,ensure_ascii=False))
