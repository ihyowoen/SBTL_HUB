import json,pathlib,concurrent.futures,requests,hashlib,re,html,datetime
from html.parser import HTMLParser
class Text(HTMLParser):
 def __init__(self): super().__init__(); self.out=[]; self.skip=0
 def handle_starttag(self,t,a):
  if t in ('script','style','noscript'):self.skip+=1
  if t in ('p','div','br','h1','h2','h3','article','section','li'):self.out.append('\n')
 def handle_endtag(self,t):
  if t in ('script','style','noscript'):self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip:self.out.append(d)
p=pathlib.Path('work/evidence');p.mkdir(exist_ok=True)
d=json.loads(next(pathlib.Path('work/cp20').glob('*FORMAL*.json')).read_text()); done={r['candidate_id'] for r in d['promotion_reassessment_ledger']}; groups={}
for r in d['decision_ledger']:
 if r['candidate_id'] not in done:groups.setdefault(r['primary_url'],[]).append(r['source_row_index'])
def fetch(item):
 u,rows=item;k=hashlib.sha256(u.encode()).hexdigest()[:16]; meta={'url':u,'rows':rows,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  r=requests.get(u,timeout=25,headers={'User-Agent':'Mozilla/5.0'});meta.update(status=r.status_code,final_url=r.url,sha256=hashlib.sha256(r.content).hexdigest(),content_type=r.headers.get('content-type'))
  (p/(k+'.raw')).write_bytes(r.content);t=Text();t.feed(r.text);txt=re.sub(r'[ \t]+',' ',''.join(t.out));txt=re.sub(r'\n\s*\n','\n',txt);(p/(k+'.txt')).write_text(txt);meta['text_chars']=len(txt)
 except Exception as e:meta['error']=str(e)
 (p/(k+'.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2));return meta
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
 out=list(ex.map(fetch,groups.items()))
pathlib.Path('work/source_fetch_manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('urls',len(out),'http200',sum(x.get('status')==200 for x in out),'errors',sum('error'in x for x in out))
