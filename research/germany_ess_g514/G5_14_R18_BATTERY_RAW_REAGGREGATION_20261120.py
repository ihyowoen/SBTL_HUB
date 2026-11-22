#!/usr/bin/env python3
"""Germany MaStR frozen snapshot: auditable BESS SSE/SEE reconciliation.

DO NOT interpret output as Fraunhofer 2026-10-13 exact reproduction when
input is BNetzA 2026-10-01 snapshot. Report source vintage separately.

For full remote data, copy G5_14_R16_MASTR_RANGE_VERIFY_20261119.py from the
prior Germany Drive archive next to this file and set --source official-remote.
For offline data, set --source /path/to/Gesamtdatenexport_YYYYMMDD.zip.
All result CSV/JSON are derived; original ZIP bytes remain unaltered.
"""
import argparse
import collections
import csv
from decimal import Decimal, InvalidOperation
import hashlib
import io
import json
from pathlib import Path
import re
import sqlite3
import sys
import zipfile

from lxml import etree

DEFAULT_URL = "https://download.marktstammdatenregister.de/Stichtag/Gesamtdatenexport_20261001_26.1.zip"
MEMBER_PATTERNS = {
    "sse": re.compile(r"(?:.*/)?AnlagenStromSpeicher(?:_\d+)?\.xml$", re.I),
    "see": re.compile(r"(?:.*/)?EinheitenStromSpeicher(?:_\d+)?\.xml$", re.I),
    "catalog": re.compile(r"(?:.*/)?Katalogwerte(?:_\d+)?\.xml$", re.I),
}
ENTRY_TAGS = {"sse": "AnlageStromSpeicher", "see": "EinheitStromSpeicher", "catalog": "Katalogwert"}
RE_SEE = re.compile(r"SEE\d{9,15}")
OPERATIONAL = "35"  # 'In Betrieb' confirmed in R06 source XML; catalog revalidated on replay.
BATTERY = "524"     # 'Batterie' confirmed in R06 source XML; catalog revalidated on replay.
CUTOFF = "2026-09-30"


def fields(element):
    return {child.tag.rsplit("}", 1)[-1]: " ".join(child.itertext()).strip()
            for child in element}


def iter_objects(archive, info, kind):
    """Streams one ZIP member. zipfile validates its CRC when read to EOF."""
    with archive.open(info) as handle:
        iterator = etree.iterparse(handle, events=("end",),
                                   tag=ENTRY_TAGS[kind], huge_tree=True,
                                   resolve_entities=False, no_network=True)
        for _, element in iterator:
            yield fields(element)
            element.clear()
            while element.getprevious() is not None:
                del element.getparent()[0]
        handle.read()  # finish ZIP member to EOF; force zipfile CRC validation


def decimal_or_none(v):
    if v is None or str(v).strip()=="":
        return None
    try:
        x=Decimal(str(v).strip().replace(",", "."))
        return x if x.is_finite() else None
    except InvalidOperation:
        return None


def con_init(path):
    con=sqlite3.connect(path)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    con.executescript("""
    CREATE TABLE IF NOT EXISTS sse(
       id TEXT PRIMARY KEY, usable_kwh TEXT, status TEXT, linked_see TEXT);
    CREATE TABLE IF NOT EXISTS see(
       id TEXT PRIMARY KEY, spe_id TEXT, country_code TEXT, status TEXT,
       technology_code TEXT, cod TEXT, gross_kw TEXT, net_kw TEXT);
    CREATE TABLE IF NOT EXISTS see_link(sse_id TEXT, see_id TEXT,
       PRIMARY KEY(sse_id,see_id));
    """)
    return con


def group_members(archive):
    names=archive.infolist()
    groups={kind: sorted([info for info in names if pat.fullmatch(info.filename)],
                         key=lambda i:i.filename) for kind,pat in MEMBER_PATTERNS.items()}
    return groups


def catalog_map(archive, infos):
    cats=collections.defaultdict(list)
    allrows=[]
    for info in infos:
        for f in iter_objects(archive,info,"catalog"):
            code=str(f.get("Id", "")); val=f.get("Wert", ""); cat=f.get("KatalogKategorieId", "")
            cats[val.casefold()].append((code,cat))
            allrows.append((code,val,cat))
    return cats,allrows


def infer_catalog(catalog_rows):
    def require(name, known=None):
        matches=[(code,value,cat) for code,value,cat in catalog_rows if value.casefold() == name.casefold()]
        if not matches:
            raise ValueError("Catalog does not contain exact value: "+name)
        if known is not None:
            matches=[r for r in matches if r[0]==known]
            if len(matches)!=1:
                raise ValueError(f"Catalog code for {name} changed/ambiguous; expected {known}, got {matches}")
        elif len(matches)!=1:
            raise ValueError(f"Catalog {name} has multiple candidate IDs: {matches}")
        return matches[0][0]
    return {"operational":require("In Betrieb",OPERATIONAL),
            "battery":require("Batterie",BATTERY),
            "de":require("Deutschland")}


def ingest(archive, groups, con):
    counts={}
    for kind in ("sse","see"):
        batch=[]; linkbatch=[]; n=0
        for info in groups[kind]:
            for f in iter_objects(archive,info,kind):
                n+=1
                if kind=="sse":
                    sid=f.get("MaStRNummer","")
                    if not sid.startswith("SSE"):
                        raise ValueError(f"Bad SSE ID {sid!r} in {info.filename}")
                    batch.append((sid,f.get("NutzbareSpeicherkapazitaet"),
                                  f.get("AnlageBetriebsstatus"),f.get("VerknuepfteEinheitenMaStRNummern","")))
                    for see_id in set(RE_SEE.findall(f.get("VerknuepfteEinheitenMaStRNummern", ""))):
                        linkbatch.append((sid,see_id))
                    if len(linkbatch)>=3000:
                        con.executemany("INSERT OR IGNORE INTO see_link VALUES (?,?)",linkbatch);linkbatch=[]
                else:
                    seeid=f.get("EinheitMastrNummer",f.get("EinheitMaStrNummer", ""))
                    if not seeid.startswith("SEE"):
                        raise ValueError(f"Bad SEE ID {seeid!r} in {info.filename}")
                    batch.append((seeid,f.get("SpeMaStRNummer"),f.get("Land"),
                                  f.get("EinheitBetriebsstatus"),f.get("Technologie"),
                                  f.get("Inbetriebnahmedatum"),f.get("Bruttoleistung"),f.get("Nettonennleistung")))
                if len(batch)>=2500:
                    if kind=="sse":
                        con.executemany("INSERT INTO sse VALUES (?,?,?,?)",batch)
                    else:
                        con.executemany("INSERT INTO see VALUES (?,?,?,?,?,?,?,?)",batch)
                    batch=[]
            con.commit()
            print(f"CRC-checked through full member read {info.filename}: total {n} {kind}",file=sys.stderr)
        if batch:
            con.executemany("INSERT INTO sse VALUES (?,?,?,?)" if kind=="sse"
                            else "INSERT INTO see VALUES (?,?,?,?,?,?,?,?)",batch)
        if linkbatch:
            con.executemany("INSERT OR IGNORE INTO see_link VALUES (?,?)",linkbatch)
        con.commit(); counts[kind]=n
    return counts


def calculate(con, code, cutoff=CUTOFF):
    # One output record per SSE, independently count eligible SEE and gross output.
    # SQL join uses the direct SEE.spe_id first, fallback to reverse SSE link where missing.
    # Critically, usable_kwh belongs to SSE, never summed per SEE row.
    query="""
    SELECT s.id, s.usable_kwh, s.status, e.id, e.cod, e.gross_kw,
           e.spe_id, e.country_code, e.status, e.technology_code
    FROM sse s JOIN see e ON e.spe_id=s.id
    WHERE e.country_code=? AND e.technology_code=? AND
          e.status=? AND s.status=? AND e.cod<=? AND e.cod !=''
    ORDER BY s.id, e.id
    """
    selected=collections.defaultdict(lambda:{"units":set(),"gross_kw":Decimal(0),"usable_kwh":None,"bad":[]})
    for sid,cap,ssstatus,seeid,cod,gross,pid,country,estatus,tech in con.execute(
            query,(code["de"],code["battery"],code["operational"],code["operational"],cutoff)):
        entry=selected[sid];entry["units"].add(seeid)
        capd=decimal_or_none(cap)
        if entry["usable_kwh"] is None: entry["usable_kwh"]=capd
        power=decimal_or_none(gross)
        if power is None or power<=0: entry["bad"].append("gross_kw_invalid")
        else: entry["gross_kw"]+=power
    classes=collections.defaultdict(lambda:{"sse":0,"units":0,"usable_kwh":Decimal(0),"gross_kw":Decimal(0)})
    rejected=collections.Counter()
    for sid,d in selected.items():
        cap=d["usable_kwh"]
        if cap is None or cap<=0:
            rejected["nonpositive_or_missing_usable_kwh"]+=1; continue
        if d["bad"]:
            rejected["gross_kw_invalid"]+=1; continue
        category="large_strictly_over_1MWh" if cap>1000 else "small_or_medium_le_1MWh"
        for label in ("all",category):
            r=classes[label];r["sse"]+=1;r["units"]+=len(d["units"]);r["usable_kwh"]+=cap;r["gross_kw"]+=d["gross_kw"]
    # Original record integrity / existence, distinct from measure validity
    orphan_direct=con.execute("SELECT COUNT(*) FROM see e WHERE e.spe_id NOT NULL AND e.spe_id!='' AND NOT EXISTS (SELECT 1 FROM sse s WHERE s.id=e.spe_id)").fetchone()[0]
    reverse_conflicts=con.execute("SELECT COUNT(*) FROM see_link l JOIN see e ON e.id=l.see_id WHERE e.spe_id IS NOT NULL AND e.spe_id!='' AND e.spe_id!=l.sse_id").fetchone()[0]
    # show distinct reverse-only SEE, allowing separate triage instead of silently counting
    reverse_only=con.execute("SELECT COUNT(DISTINCT l.see_id) FROM see_link l LEFT JOIN see e ON e.id=l.see_id WHERE e.id IS NULL OR e.spe_id IS NULL OR e.spe_id='' ").fetchone()[0]
    return {"cutoff":cutoff,"codes":code,
            "aggregates":{k:{"sse_installations":v["sse"],"see_units":v["units"],
                             "capacity_GWh":str(v["usable_kwh"]/Decimal(1000000)),
                             "gross_output_GW":str(v["gross_kw"]/Decimal(1000000))}
                          for k,v in classes.items()},
            "rejected":dict(rejected),"orphan_direct_links":orphan_direct,
            "reverse_link_conflicts":reverse_conflicts,"reverse_only_see":reverse_only,
            "excluded_planned_and_non_battery_by_filters":True,
            "fraunhofer_2026_10_13_exact_comparability":False,
            "fraunhofer_2026_10_13_plausibility_filter_reproduction":False}


def execute(source,output_dir):
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    if source=="official-remote":
        from G5_14_R16_MASTR_RANGE_VERIFY_20261119 import HttpRangeFile
        fileobj=HttpRangeFile(DEFAULT_URL)
    else: fileobj=source
    dbpath=out/"mastr_r18_battery.sqlite"
    if dbpath.exists():
        raise FileExistsError(f"Existing output database; use new --out, never double-ingest: {dbpath}")
    con=con_init(dbpath)
    with zipfile.ZipFile(fileobj) as archive:
        groups=group_members(archive)
        if not groups["sse"] or not groups["see"] or not groups["catalog"]:
            raise ValueError({"fatal_missing_member_groups": {k:len(v) for k,v in groups.items()}})
        if source=="official-remote" and (len(groups["sse"])!=29 or len(groups["see"])!=29):
            raise ValueError("Frozen 2026-10 official source unexpectedly not 29+29 parts")
        _,rows=catalog_map(archive,groups["catalog"])
        codes=infer_catalog(rows)
        counts=ingest(archive,groups,con)
    result=calculate(con,codes)
    result.update({"source": DEFAULT_URL if source=="official-remote" else str(source),
                   "source_frozen_vintage":"2026-10-01" if source=="official-remote" else "fixture_or_local",
                   "parsed_counts":counts,
                   "member_counts":{k:len(v) for k,v in groups.items()},
                   "method":"SSE capacity / SEE gross; strict >1000kWh; Germany+Batterie+In Betrieb+COD<=Sep30",
                   "source_export_crc":"ZIP member complete read; zipfile CRC checks automatically"})
    (out/"G5_14_R18_BATTERY_QC.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    with (out/"G5_14_R18_BATTERY_CLASSES.csv").open("w",newline="",encoding="utf-8") as h:
        writer=csv.writer(h);writer.writerow(["class","sse_installations","see_units","capacity_GWh","gross_output_GW"])
        for name,v in result["aggregates"].items(): writer.writerow([name,*[v[x] for x in ("sse_installations","see_units","capacity_GWh","gross_output_GW")]])
    con.close();return result


def write_fixture(path):
    # synthetic only, never public 2026 Germany observations
    obj={"sse":[
      ("SSE100000001",600,35,"SEE100000001,SEE100000002"),
      ("SSE100000002",1200,35,"SEE100000003"),
      ("SSE100000003",1000,35,"SEE100000004"),
      ("SSE100000004",9000,35,"SEE100000005"),
      ("SSE100000005",1000,35,"SEE100000006"),
      ("SSE100000006",2000,4,"SEE100000007")],
      "see":[
      ("SEE100000001","SSE100000001",25,35,524,"2024-01-01",400),
      ("SEE100000002","SSE100000001",25,35,524,"2024-01-01",100),
      ("SEE100000003","SSE100000002",25,35,524,"2026-08-01",900),
      ("SEE100000004","SSE100000003",25,35,524,"2026-09-01",500),
      ("SEE100000005","SSE100000004",26,35,524,"2026-09-01",2000),
      ("SEE100000006","SSE100000005",25,35,1537,"2026-09-01",100),
      ("SEE100000007","SSE100000006",25,4,524,"2027-01-01",100)],
      "catalog":[(35,"In Betrieb",1),(524,"Batterie",2),(25,"Deutschland",3)]}
    from xml.etree.ElementTree import Element, SubElement, tostring
    def xml_make(root_name,entry_name,records):
        root=Element(root_name)
        for record in records:
            e=SubElement(root,entry_name)
            if entry_name=="AnlageStromSpeicher":
                r=dict(zip(("MaStRNummer","NutzbareSpeicherkapazitaet","AnlageBetriebsstatus","VerknuepfteEinheitenMaStRNummern"),record))
            elif entry_name=="EinheitStromSpeicher":
                r=dict(zip(("EinheitMastrNummer","SpeMaStRNummer","Land","EinheitBetriebsstatus","Technologie","Inbetriebnahmedatum","Bruttoleistung"),record))
            else:r=dict(zip(("Id","Wert","KatalogKategorieId"),record))
            for k,v in r.items():SubElement(e,k).text=str(v)
        return tostring(root,encoding="utf-8",xml_declaration=True)
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("AnlagenStromSpeicher.xml",xml_make("AnlagenStromSpeicher","AnlageStromSpeicher",obj["sse"]))
        z.writestr("EinheitenStromSpeicher.xml",xml_make("EinheitenStromSpeicher","EinheitStromSpeicher",obj["see"]))
        z.writestr("Katalogwerte.xml",xml_make("Katalogwerte","Katalogwert",obj["catalog"]))


def main():
    p=argparse.ArgumentParser();p.add_argument("--source",default="official-remote")
    p.add_argument("--out",default="G5_14_R18_output");p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:
        tmp=Path(a.out);tmp.mkdir(parents=True,exist_ok=True)
        fixture=tmp/"synthetic_fixture_NOT_REAL_DATA.zip";write_fixture(fixture)
        import shutil
        testdir=tmp/"test_run"
        if testdir.exists(): shutil.rmtree(testdir)  # only synthetic test path
        r=execute(str(fixture),testdir)
        assert r["aggregates"]["all"]=={"sse_installations":3,"see_units":4,"capacity_GWh":"0.0028","gross_output_GW":"0.0019"},r
        assert r["aggregates"]["large_strictly_over_1MWh"]=={"sse_installations":1,"see_units":1,"capacity_GWh":"0.0012","gross_output_GW":"0.0009"},r
        assert r["reverse_link_conflicts"]==0 and r["orphan_direct_links"]==0
        print("SYNTHETIC_QC_PASS: 6 SSE / 7 SEE; German operating battery 3 SSE / 4 SEE; 2.8 MWh, 1.9 MW; >1MWh 1.2 MWh /0.9MW, boundary=1000 excluded")
    else:
        r=execute(a.source,a.out)
        print(json.dumps(r,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
