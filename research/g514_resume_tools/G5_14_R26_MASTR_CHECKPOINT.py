#!/usr/bin/env python3
"""R26: bounded, resumable MaStR extraction/aggregation, using frozen R23 inventory.
The verified R23 parser is imported unchanged. A full ZIP is not needed remotely.
Persistent work dir: preserve it (including chunks and SQLite) across invocations.
A failed or capped invocation is NOT a country census. Never run two concurrently.
"""
import argparse, collections, fcntl, hashlib, http.client, io, json, os, re
import sqlite3, sys, time, urllib.error, urllib.request, zipfile
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

URL='https://download.marktstammdatenregister.de/Stichtag/Gesamtdatenexport_20261001_26.1.zip'
EXPECTED_SIZE=3218297640
BLOCK=4*1024*1024
CATEGORIES={'catalog':'Katalogwerte','sse':'AnlagenStromSpeicher','see':'EinheitenStromSpeicher'}
EXPECTED_CODES={'operational':('35','In Betrieb','4'),'battery':('524','Batterie','29'),'de':('84','Deutschland','6')}
class BudgetStop(RuntimeError): pass
class IdentityError(RuntimeError): pass

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def atomic(p,data):
    tmp=p.with_name(p.name+'.tmp')
    with tmp.open('wb') as f:
        f.write(data);f.flush();os.fsync(f.fileno())
    os.replace(tmp,p)
def json_write(p,obj):atomic(p,(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode())

def retry_after(e):
    v=getattr(e,'headers',{}).get('Retry-After') if getattr(e,'headers',None) else None
    if not v:return 0
    try:return max(0,int(v))
    except ValueError:
        try:return max(0,(parsedate_to_datetime(v)-datetime.now(timezone.utc)).total_seconds())
        except (ValueError,TypeError):return 0

class CachedRange(io.RawIOBase):
    """Fixed non-overlapping range blocks: verify exact validator, range and length.
    Only fully verified bytes are cached; cache reuse requires SHA-256 readback.
    Archived R23 strong ETag used directly: no repeated HEAD/ZIP inventory probes.
    """
    def __init__(self,url,length,etag,cache,max_requests=50,block=BLOCK,sleep=time.sleep):
        super().__init__()
        if not etag or etag.startswith('W/') or not etag.startswith('"') or not etag.endswith('"'):
            raise IdentityError('Strong archived ETag required for remote resume')
        self.url,self.length,self.etag,self.block=url,int(length),etag,block
        self.cache=Path(cache);self.cache.mkdir(parents=True,exist_ok=True)
        self.pos=0;self.requests=0;self.cache_hits=0;self.max_requests=max_requests;self.sleep=sleep
        meta={'url':url,'length':self.length,'etag':etag,'block':block}
        p=self.cache/'identity.json'
        if p.exists() and json.loads(p.read_text())!=meta:raise IdentityError('Cache identity changed')
        if not p.exists():json_write(p,meta)
        self.last_index=None;self.last_data=None
    def seekable(self):return True
    def readable(self):return True
    def tell(self):return self.pos
    def seek(self,offset,whence=io.SEEK_SET):
        if whence==io.SEEK_CUR:offset+=self.pos
        elif whence==io.SEEK_END:offset+=self.length
        elif whence!=io.SEEK_SET:raise ValueError(whence)
        if not 0<=offset<=self.length:raise ValueError('Invalid seek')
        self.pos=offset;return offset
    def _get(self,i):
        if i==self.last_index:return self.last_data
        start=i*self.block;end=min(self.length,start+self.block)-1;need=end-start+1
        p=self.cache/f'{i:08d}.bin';q=self.cache/f'{i:08d}.json'
        if p.exists() and q.exists():
            b=p.read_bytes();receipt=json.loads(q.read_text())
            if len(b)!=need or receipt!={'length':need,'sha256':sha_bytes(b)}:raise IdentityError(f'Cached block {i} corrupt; investigate, no silent redownload')
            self.cache_hits+=1
        else:
            # One incomplete atomic pair may remain after a crash. Do not treat it as verified.
            if p.exists() or q.exists():raise IdentityError(f'Incomplete cache pair {i}; quarantine explicitly')
            req=urllib.request.Request(self.url,headers={'Range':f'bytes={start}-{end}','If-Range':self.etag,'Accept-Encoding':'identity','User-Agent':'Research-MaStR-G514/2.0'})
            for attempt in range(3):
                if self.requests>=self.max_requests:raise BudgetStop('Bounded range-request budget exhausted')
                self.requests+=1
                try:
                    with urllib.request.urlopen(req,timeout=60) as r:
                        if r.status!=206:raise IdentityError(f'Expected 206, received {r.status}; do not consume full body')
                        if r.headers.get('Content-Range')!=f'bytes {start}-{end}/{self.length}':raise IdentityError('Content-Range mismatch')
                        if r.headers.get('ETag')!=self.etag:raise IdentityError('Original ETag absent or changed')
                        if r.headers.get('Content-Encoding','identity').lower()!='identity':raise IdentityError('Non-identity transport encoding')
                        b=r.read(need+1)
                        if len(b)!=need:raise http.client.IncompleteRead(b,need-len(b))
                    break
                except urllib.error.HTTPError as e:
                    if e.code not in (429,500,502,503,504):raise
                    wait=retry_after(e)
                    if wait>60:raise BudgetStop('Provider Retry-After exceeds bounded wait; stop') from e
                    if attempt==2:raise BudgetStop(f'Provider HTTP {e.code} exhausted 3 attempts') from e
                    self.sleep(max(wait,5*(2**attempt)))
                except (OSError,http.client.HTTPException) as e:
                    if attempt==2:raise BudgetStop('Transport failed after 3 attempts') from e
                    self.sleep(5*(2**attempt))
            atomic(p,b);json_write(q,{'length':need,'sha256':sha_bytes(b)})
        self.last_index,self.last_data=i,b
        return b
    def read(self,size=-1):
        n=self.length-self.pos if size is None or size<0 else min(size,self.length-self.pos)
        parts=[]
        while n>0:
            i,offset=divmod(self.pos,self.block);b=self._get(i);k=min(n,len(b)-offset)
            parts.append(b[offset:offset+k]);self.pos+=k;n-=k
        return b''.join(parts)

def inventory_check(archive,groups,inventory):
    for kind,name in CATEGORIES.items():
        expected=inventory['groups'][name]
        got=[{'name':i.filename,'crc32':f'{i.CRC:08x}','compressed':i.compress_size} for i in groups[kind]]
        if len(got)!=expected['count'] or sorted(got,key=lambda x:x['name'])!=sorted(expected['members'],key=lambda x:x['name']):
            raise IdentityError('Frozen central-directory member identity differs: '+kind)
        if sum(i.file_size for i in groups[kind])!=expected['uncompressed_bytes']:raise IdentityError('Uncompressed member sizes differ: '+kind)
    if len(archive.infolist())!=inventory['total_members']:raise IdentityError('Total ZIP member count changed')

def setup(parser,db,identity):
    con=parser.con_init(db)
    con.execute('CREATE TABLE IF NOT EXISTS r26_meta (key TEXT PRIMARY KEY,value TEXT NOT NULL)')
    con.execute('CREATE TABLE IF NOT EXISTS r26_members (name TEXT PRIMARY KEY,kind TEXT NOT NULL,crc TEXT NOT NULL,rows INTEGER NOT NULL)')
    con.execute('CREATE TABLE IF NOT EXISTS r26_catalog (id TEXT PRIMARY KEY,value TEXT,category TEXT)')
    old=con.execute("SELECT value FROM r26_meta WHERE key='identity'").fetchone()
    val=json.dumps(identity,sort_keys=True)
    if old and old[0]!=val:con.close();raise IdentityError('Database source/parser identity changed; never mix vintages')
    if not old:
        if any(con.execute(f'SELECT count(*) FROM {t}').fetchone()[0] for t in ('sse','see','see_link','r26_members')):
            con.close();raise IdentityError('Unowned database already contains records')
        con.execute('INSERT INTO r26_meta VALUES (?,?)',('identity',val));con.commit()
    return con

def ingest_member(parser,con,archive,kind,info):
    """One member + receipt in one transaction; no partial rows after failure/CRC error."""
    old=con.execute('SELECT kind,crc,rows FROM r26_members WHERE name=?',(info.filename,)).fetchone()
    crc=f'{info.CRC:08x}'
    if old:
        if old[:2]!=(kind,crc):raise IdentityError('Checkpoint receipt mismatch')
        return False,old[2]
    n=0;rows=[];edges=[]
    def flush():
        table={'catalog':'r26_catalog','sse':'sse','see':'see'}[kind]
        sql={'catalog':'?,?,?','sse':'?,?,?,?','see':'?,?,?,?,?,?,?,?'}[kind]
        if rows:con.executemany(f'INSERT INTO {table} VALUES ({sql})',rows);rows.clear()
        if edges:con.executemany('INSERT OR IGNORE INTO see_link VALUES (?,?)',edges);edges.clear()
    con.execute('BEGIN IMMEDIATE')
    try:
        for f in parser.iter_objects(archive,info,kind):
            n+=1
            if kind=='catalog':rows.append((f['Id'],f['Wert'],f['KatalogKategorieId']))
            elif kind=='sse':
                sid=f.get('MaStRNummer','')
                if not sid.startswith('SSE'):raise ValueError('Bad SSE ID')
                links=f.get('VerknuepfteEinheitenMaStRNummern','')
                rows.append((sid,f.get('NutzbareSpeicherkapazitaet'),f.get('AnlageBetriebsstatus'),links))
                edges.extend((sid,s) for s in set(parser.RE_SEE.findall(links)))
            else:
                sid=f.get('EinheitMastrNummer',f.get('EinheitMaStrNummer',''))
                if not sid.startswith('SEE'):raise ValueError('Bad SEE ID')
                rows.append((sid,f.get('SpeMaStRNummer'),f.get('Land'),f.get('EinheitBetriebsstatus'),f.get('Technologie'),f.get('Inbetriebnahmedatum'),f.get('Bruttoleistung'),f.get('Nettonennleistung')))
            if len(rows)>=2500 or len(edges)>=3000:flush()
        # iter_objects reads to EOF, forcing ZIP CRC before receipt/commit.
        if not n:raise ValueError('Empty parsed member')
        flush();con.execute('INSERT INTO r26_members VALUES (?,?,?,?)',(info.filename,kind,crc,n));con.commit()
    except BaseException:con.rollback();raise
    return True,n

def codes(con):
    actual=set(con.execute('SELECT id,value,category FROM r26_catalog'))
    if not set(EXPECTED_CODES.values()).issubset(actual):raise IdentityError('Official category+ID+name mismatch')
    return {k:v[0] for k,v in EXPECTED_CODES.items()}

def run(parser,inventory,work,source='official-remote',max_members=4,max_requests=50,fixture=False):
    work=Path(work);work.mkdir(parents=True,exist_ok=True)
    if max_members<1 or max_requests<1:raise ValueError('Positive bounded budgets required')
    with (work/'run.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if not fixture:
            if inventory['url']!=URL or inventory['bytes']!=EXPECTED_SIZE or any(inventory['groups'][n]['count']!=c for n,c in [('AnlagenStromSpeicher',29),('EinheitenStromSpeicher',29),('Katalogwerte',1)]):raise IdentityError('Wrong frozen official inventory')
        if source=='official-remote':
            raw=CachedRange(inventory['url'],inventory['bytes'],inventory['etag'],work/'chunks',max_requests)
            identity={'remote_url':inventory['url'],'etag':inventory['etag'],'bytes':inventory['bytes']}
        else:
            raw=Path(source)
            if raw.stat().st_size!=inventory['bytes']:raise IdentityError('Local ZIP length mismatch')
            identity={'local_sha256':sha_file(raw),'bytes':inventory['bytes']}
        identity.update({'inventory_sha256':sha_bytes(json.dumps(inventory,sort_keys=True).encode()),'parser_sha256':sha_file(parser.__file__),'checkpoint_code_sha256':sha_file(__file__),'fixture':fixture})
        con=None;new=0;failure=None
        try:
            with zipfile.ZipFile(raw) as z:
                groups=parser.group_members(z);inventory_check(z,groups,inventory)
                con=setup(parser,work/'checkpoint.sqlite',identity)
                for kind in ('catalog','sse','see'):
                    for info in groups[kind]:
                        if con.execute('SELECT 1 FROM r26_members WHERE name=?',(info.filename,)).fetchone():continue
                        if new>=max_members:raise BudgetStop('Per-invocation new-member cap reached')
                        fresh,count=ingest_member(parser,con,z,kind,info);new+=int(fresh)
                        print('CRC_MEMBER_COMMITTED',kind,info.filename,count,flush=True)
                    if kind=='catalog':codes(con)
                result=parser.calculate(con,codes(con))
                result.update({'source_identity':identity,'source_frozen_vintage':'SYNTHETIC_NOT_REAL' if fixture else '2026-10-01','completed_members':dict(con.execute('SELECT kind,count(*) FROM r26_members GROUP BY kind')),'fraunhofer_same_vintage':False})
                json_write(work/'RESULT.json',result)
        except Exception as e:failure=f'{type(e).__name__}: {e}'
        finally:
            done=dict(con.execute('SELECT kind,count(*) FROM r26_members GROUP BY kind')) if con else {}
            if con:con.close()
            receipt={'identity':identity,'new_crc_members':new,'completed_members':done,'error':failure,'full_complete':failure is None and all(done.get(k,0)==inventory['groups'][n]['count'] for k,n in CATEGORIES.items()),'request_attempts':getattr(raw,'requests',0),'verified_cache_hits':getattr(raw,'cache_hits',0),'fixture':fixture}
            json_write(work/'RUN_RECEIPT.json',receipt)
            if isinstance(raw,CachedRange):raw.close()
        return receipt

def main():
    p=argparse.ArgumentParser();p.add_argument('--parser',type=Path,required=True);p.add_argument('--inventory',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--source',default='official-remote');p.add_argument('--max-members',type=int,default=4);p.add_argument('--max-requests',type=int,default=50);a=p.parse_args()
    import importlib.util
    spec=importlib.util.spec_from_file_location('r23_parser',a.parser);parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
    inv=json.loads(a.inventory.read_text());r=run(parser,inv,a.work,a.source,a.max_members,a.max_requests)
    print(json.dumps(r,indent=2));sys.exit(0 if r['full_complete'] else 2)
if __name__=='__main__':main()
