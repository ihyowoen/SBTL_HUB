import { useState, useEffect, useRef, useMemo } from "react";

const LOGO_D = "/data/logo.png";
const CD = {
  newsletter:[],
  webtoon:[],
};

const WEBTOON_COLLECTIONS = [
  {
    id:"lfp-uncomfortable-truths",
    title:"LFP의 불편한 진실",
    subtitle:"LFP를 둘러싼 대표적 오해와 비용 구조를 웹툰 형식으로 정리한 시리즈",
    badge:"FLAGSHIP SERIES",
    color:"#F85149",
    landingUrl:"/webtoon/lfp-uncomfortable-truths.html",
    status:"NOW LIVE",
    hook:"좋은 배터리일 수 있다. 그런데 너무 쉽게 보면 핵심을 놓친다.",
    description:"EP.01부터 Bonus.01까지, LFP 안전성 인식과 비용 구조를 단계적으로 따라가는 시리즈입니다.",
    items:[
      {id:101,title:"EP.01 LFP의 두 가지 착각",subtitle:"좋은 배터리일 수 있다. 그런데 너무 쉽게 보면 핵심을 놓친다.",date:"2026.04.05",isNew:true,color:"#F85149",likes:0,url:"/webtoon/lfp-two-misconceptions-ep1.html",tag:"START"},
      {id:102,title:"EP.02 덜 타 보인다고, 덜 위험한 건 아니다",subtitle:"보이는 화재 위험과 보이지 않는 off-gas 위험은 같은 말이 아니다.",date:"2026.04.05",isNew:true,color:"#D29922",likes:0,url:"/webtoon/lfp-two-misconceptions-ep2.html",tag:"PART 2"},
      {id:103,title:"BONUS.01 누가 진짜 돈을 내나?",subtitle:"끝날 때 비용은 존재한다. 그 돈을 누가 떠안는지 묻는 보너스 에피소드.",date:"2026.04.05",isNew:true,color:"#58A6FF",likes:0,url:"/webtoon/who-pays-bonus1.html",tag:"BONUS"}
    ]
  }
];
const CATS=[{key:"all",label:"HOME",icon:"🔋"},{key:"news",label:"NEWS",icon:"📰"},{key:"webtoon",label:"TOON",icon:"🎨"},{key:"tracker",label:"TRCK",icon:"📊"},{key:"chatbot",label:"AI",icon:"🤖"}];
const CM={newsletter:{emoji:"📨",label:"뉴스레터"},webtoon:{emoji:"🎨",label:"웹툰"}};
const SC={ACTIVE:"#F85149",UPCOMING:"#D29922",WATCH:"#388BFD",DONE:"#7D8590"};
const SL={ACTIVE:"ACTIVE",UPCOMING:"UPCOMING",WATCH:"WATCH",DONE:"DONE"};
const sigC={t:"#F85149",h:"#D29922",m:"#388BFD"};
const sigL={t:"TOP",h:"HIGH",m:"MID"};
const regFlag={US:"🇺🇸",KR:"🇰🇷",EU:"🇪🇺",CN:"🇨🇳",JP:"🇯🇵",GL:"🌐","US/KR":"🇺🇸"};
const fmtDate = (date) => {
  if (!date) return "-";
  const s = String(date).trim();
  const m = s.match(/^(\d{4})[.-](\d{2})[.-](\d{2})/);
  if (m) return `${m[1]}.${m[2]}.${m[3]}`;
  return s;
};
const pct=(num,total)=>`${Math.max(0,Math.min(100,((Number(num)||0)/Math.max(1,Number(total)||0))*100))}%`;

const T=(dk=true)=>dk?{
  bg:"#0D1117",card:"#161B26",card2:"#1C2333",tx:"#E6EDF3",sub:"#7D8590",
  brd:"#21293A",sh:"0 2px 8px rgba(0,0,0,0.4)",cyan:"#58A6FF",green:"#3FB950",
}:{
  bg:"#F4F6FA",card:"#FFFFFF",card2:"#F8F9FC",tx:"#1a1a2a",sub:"#6b7280",
  brd:"#e0e3ea",sh:"0 2px 10px rgba(0,0,0,0.06)",cyan:"#2d5a8e",green:"#16a34a",
};

function useKnowledgeBase(){const[cards,setCards]=useState([]);const[faq,setFaq]=useState([]);const[loading,setLoading]=useState(true);
  useEffect(()=>{Promise.all([fetch("/data/cards.json").then(r=>r.json()).then(d=>d.cards||d).catch(()=>[]),fetch("/data/faq.json").then(r=>r.json()).catch(()=>[])]).then(([c,f])=>{setCards(c);setFaq(f);setLoading(false);});},[]);
  return{cards,faq,loading,cardCount:cards.length,faqCount:faq.length};}


function useTrackerData(){
  const [raw,setRaw]=useState(null);
  const [loading,setLoading]=useState(true);
  useEffect(()=>{
    fetch("/data/tracker_data.json")
      .then(r=>r.json())
      .then(setRaw)
      .catch(()=>setRaw(null))
      .finally(()=>setLoading(false));
  },[]);
  const normalized=useMemo(()=>{
    const fallback={meta:{lastUpdated:"-",totalItems:0},summary:{ACTIVE:0,UPCOMING:0,WATCH:0,DONE:0},regions:[],upcoming:[],items:[]};
    if(!raw||!Array.isArray(raw.items)) return fallback;
    const items=raw.items;
    const meta={
      lastUpdated: raw.meta?.lastUpdated || "-",
      totalItems: Number(raw.meta?.totalItems ?? items.length) || items.length,
      version: raw.meta?.version || "1.0"
    };
    const summary=items.reduce((acc,item)=>{const k=item?.s; if(acc[k]!==undefined) acc[k]+=1; return acc;},{ACTIVE:0,UPCOMING:0,WATCH:0,DONE:0});
    const regionName={NA:"북미",EU:"유럽",CN:"중국",KR:"한국",JP:"일본",GL:"글로벌"};
    const regionFlag={NA:"🇺🇸",EU:"🇪🇺",CN:"🇨🇳",KR:"🇰🇷",JP:"🇯🇵",GL:"🌐"};
    const regions=["NA","EU","CN","KR","JP","GL"].map(code=>{
      const list=items.filter(i=>i.r===code);
      if(!list.length) return null;
      return {
        code,
        flag:regionFlag[code]||"🌐",
        name:regionName[code]||code,
        total:list.length,
        ACTIVE:list.filter(i=>i.s==="ACTIVE").length
      };
    }).filter(Boolean);
    const upcoming=items
      .filter(i=>i.s==="UPCOMING")
      .sort((a,b)=>String(a.dt||"").localeCompare(String(b.dt||"")))
      .slice(0,8)
      .map(i=>({date:i.dt||"-",title:i.t,region:i.r}));
    return {meta,summary,regions,upcoming,items};
  },[raw]);
  return {tracker:normalized,loading};
}


function searchCards(cards,q){const ws=q.toLowerCase().replace(/[?!.,]/g,"").split(/\s+/).filter(w=>w.length>=2);if(!ws.length)return[];
  return cards.map(c=>{let sc=0;const tl=c.T.toLowerCase(),gl=(c.g||"").toLowerCase(),ks=c.k||[];for(const w of ws){if(tl.includes(w))sc+=10;if(gl.includes(w))sc+=5;if(ks.some(k=>k.includes(w)||w.includes(k)))sc+=8;}if(c.s==="t")sc*=2;else if(c.s==="h")sc*=1.5;return{...c,sc};}).filter(c=>c.sc>0).sort((a,b)=>b.sc-a.sc).slice(0,3);}

/* News Feed Item */
function NewsItem({card,dark}) {
  const t=T(dark);const sig=card.s;const flag=regFlag[card.r]||"🌐";const dateStr=card.d?card.d.slice(5).replace("-","."):"";
  return (<div onClick={()=>card.url&&window.open(card.url,"_blank")} style={{background:t.card2,borderRadius:10,padding:"11px 13px",borderLeft:`3px solid ${sigC[sig]}`,border:`1px solid ${t.brd}`,cursor:card.url?"pointer":"default"}}>
    <div style={{display:"flex",alignItems:"center",gap:6,marginBottom:4}}>
      <span style={{fontSize:8,fontWeight:800,color:sigC[sig],background:sigC[sig]+"20",padding:"2px 6px",borderRadius:3,fontFamily:"'JetBrains Mono',monospace",letterSpacing:1}}>{sigL[sig]}</span>
      <span style={{fontSize:9,color:t.sub,fontFamily:"'JetBrains Mono',monospace"}}>{flag} {dateStr}</span>
      {card.src&&<span style={{fontSize:8,color:t.sub,marginLeft:"auto",fontFamily:"'JetBrains Mono',monospace"}}>{card.src}</span>}
    </div>
    <h3 style={{fontSize:13,fontWeight:700,color:t.tx,margin:0,lineHeight:1.4}}>{card.T}</h3>
    {card.sub&&<p style={{fontSize:11,color:t.sub,margin:"3px 0 0",lineHeight:1.3}}>{card.sub}</p>}
    {card.url&&<div style={{marginTop:5}}><span style={{fontSize:9,color:t.cyan,fontFamily:"'JetBrains Mono',monospace"}}>&gt; open source →</span></div>}
  </div>);
}

/* Home */
function Home({onNav,kb,tracker,dark}) {
  const t=T(dark);const[filter,setFilter]=useState("all");const[showCount,setShowCount]=useState(15);const[search,setSearch]=useState("");
  const featured=WEBTOON_COLLECTIONS[0];
  const sigCounts={t:kb.cards.filter(c=>c.s==="t").length,h:kb.cards.filter(c=>c.s==="h").length,m:kb.cards.filter(c=>c.s==="m").length};
  const regCounts={KR:kb.cards.filter(c=>c.r==="KR").length,US:kb.cards.filter(c=>c.r==="US").length,CN:kb.cards.filter(c=>c.r==="CN").length,EU:kb.cards.filter(c=>c.r==="EU").length,JP:kb.cards.filter(c=>c.r==="JP").length};
  const latestTop=kb.cards.filter(c=>c.s==="t").slice(0,3);
  let filtered=filter==="all"?kb.cards:filter==="top"?kb.cards.filter(c=>c.s==="t"):filter==="high"?kb.cards.filter(c=>c.s==="h"):kb.cards.filter(c=>c.r===filter);
  if(search){const sw=search.toLowerCase();filtered=filtered.filter(c=>c.T.toLowerCase().includes(sw)||(c.sub||"").toLowerCase().includes(sw)||(c.g||"").toLowerCase().includes(sw));}
  const visible=filtered.slice(0,showCount);
  const dates=[...new Set(visible.map(c=>c.d))];
  return (<div style={{padding:"0 14px 120px",display:"flex",flexDirection:"column",gap:12}}>
    <div style={{background:`linear-gradient(135deg, ${dark?"#151B2B":"#ffffff"}, ${dark?"#1F2840":"#EEF3FF"})`,borderRadius:18,padding:"18px 16px",border:`1px solid ${dark?"#2C3550":t.brd}`,boxShadow:t.sh}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",gap:12}}>
        <div style={{flex:1,minWidth:0}}>
          <div style={{display:"flex",alignItems:"center",gap:8,flexWrap:"wrap",marginBottom:10}}>
            <span style={{fontSize:9,fontWeight:900,color:t.cyan,background:dark?"rgba(88,166,255,0.14)":"rgba(45,90,142,0.10)",padding:"4px 8px",borderRadius:999,fontFamily:"'JetBrains Mono',monospace"}}>SBTL CONTENT HUB</span>
            <span style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace"}}>BATTERY · ESS · EV</span>
          </div>
          <div style={{fontSize:24,fontWeight:900,color:t.tx,lineHeight:1.2}}>SBTL Strategic Intelligence Brief</div>
          <div style={{fontSize:12,color:t.sub,lineHeight:1.65,marginTop:8}}>배터리·ESS·EV 밸류체인을 중심으로 정책, 공급망, 기술, 기업 이슈를 선별해 정리하는 인텔리전스 허브. C-level, 투자자, 산업 실무자가 핵심만 빠르게 확인할 수 있도록 설계했습니다.</div>
        </div>
        <div style={{width:56,height:56,borderRadius:16,background:dark?"rgba(88,166,255,0.12)":"rgba(88,166,255,0.08)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:28,flexShrink:0}}>🏢</div>
      </div>
      <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:8,marginTop:14}}>
        {[
          {label:"CARDS",value:kb.cardCount},
          {label:"FAQ",value:kb.faqCount},
          {label:"REGIONS",value:5},
          {label:"TRACKER",value:tracker.meta.totalItems},
        ].map(item=>(<div key={item.label} style={{background:dark?"rgba(10,14,20,0.55)":"rgba(255,255,255,0.88)",border:`1px solid ${t.brd}`,borderRadius:12,padding:"10px 8px",textAlign:"center"}}><div style={{fontSize:16,fontWeight:900,color:t.tx,fontFamily:"'JetBrains Mono',monospace"}}>{item.value}</div><div style={{fontSize:9,color:t.sub,fontFamily:"'JetBrains Mono',monospace",marginTop:4}}>{item.label}</div></div>))}
      </div>
      <div style={{display:"flex",gap:8,marginTop:14}}>
        <button onClick={()=>onNav("news")} style={{flex:1,border:"none",borderRadius:10,padding:"10px 12px",background:t.cyan,color:"#000",fontSize:11,fontWeight:900,cursor:"pointer",fontFamily:"'JetBrains Mono',monospace"}}>OPEN NEWS</button>
        <button onClick={()=>onNav("tracker")} style={{flex:1,border:`1px solid ${t.brd}`,borderRadius:10,padding:"10px 12px",background:"transparent",color:t.tx,fontSize:11,fontWeight:900,cursor:"pointer",fontFamily:"'JetBrains Mono',monospace"}}>OPEN TRACKER</button>
      </div>
    </div>

    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:8}}>
      <div style={{background:t.card2,borderRadius:14,padding:"14px",border:`1px solid ${t.brd}`}}>
        <div style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace",marginBottom:6}}>WHAT WE COVER</div>
        <div style={{fontSize:16,fontWeight:900,color:t.tx,lineHeight:1.3}}>핵심 이슈만 남긴 카드형 인사이트</div>
        <div style={{fontSize:11,color:t.sub,lineHeight:1.55,marginTop:6}}>정책·공급망·기술·기업 뉴스를 카드 단위로 빠르게 훑고, 필요한 항목만 깊게 읽을 수 있습니다.</div>
      </div>
      <div style={{background:t.card2,borderRadius:14,padding:"14px",border:`1px solid ${t.brd}`}}>
        <div style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace",marginBottom:6}}>AUDIENCE</div>
        <div style={{fontSize:16,fontWeight:900,color:t.tx,lineHeight:1.3}}>경영진·투자자·산업 실무자를 위한 화면</div>
        <div style={{fontSize:11,color:t.sub,lineHeight:1.55,marginTop:6}}>지표와 변화만 먼저 보고, 상세 근거는 카드·트래커·웹툰으로 이어지는 구조를 제공합니다.</div>
      </div>
    </div>

    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:8}}>
      <div onClick={()=>onNav("webtoon")} style={{background:t.card2,borderRadius:14,padding:"14px",border:`1px solid ${t.brd}`,cursor:"pointer"}}>
        <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",gap:8}}>
          <div>
            <div style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace",marginBottom:6}}>FEATURED SERIES</div>
            <div style={{fontSize:18,fontWeight:900,color:t.tx,lineHeight:1.3}}>{featured.title}</div>
          </div>
          <div style={{fontSize:24}}>📁</div>
        </div>
        <div style={{fontSize:11,color:t.sub,lineHeight:1.55,marginTop:8}}>LFP를 둘러싼 대표적 오해와 비용 구조를 웹툰 형식으로 정리한 시리즈.</div>
        <div style={{display:"flex",gap:6,flexWrap:"wrap",marginTop:10}}>{featured.items.map(item=><span key={item.id} style={{fontSize:9,color:t.tx,background:dark?"rgba(255,255,255,0.06)":"rgba(0,0,0,0.04)",padding:"5px 8px",borderRadius:999,fontFamily:"'JetBrains Mono',monospace"}}>{item.tag}</span>)}</div>
      </div>
      <div onClick={()=>onNav("chatbot")} style={{background:t.card2,borderRadius:14,padding:"14px",border:`1px solid ${dark?"#2a4060":t.brd}`,cursor:"pointer"}}>
        <div style={{display:"flex",alignItems:"center",gap:10}}>
          <img src="/data/kang.png" alt="" style={{width:34,height:34,borderRadius:17}} onError={e=>{e.target.style.display="none"}}/>
          <div>
            <div style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace",marginBottom:4}}>AI DESK</div>
            <div style={{fontSize:16,fontWeight:900,color:t.tx}}>강차장의 배터리 상담소</div>
          </div>
        </div>
        <div style={{fontSize:11,color:t.sub,lineHeight:1.55,marginTop:8}}>FAQ와 카드 데이터를 바탕으로 빠르게 맥락을 찾고, 관련 카드를 다시 탐색할 수 있습니다.</div>
        <div style={{fontSize:9,color:t.sub,fontFamily:"'JetBrains Mono',monospace",marginTop:10}}>FAQ {kb.faqCount} · CARDS {kb.cardCount}</div>
      </div>
    </div>

    <div style={{background:t.card2,borderRadius:14,padding:"14px 16px",border:`1px solid ${t.brd}`}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",gap:8,marginBottom:10}}>
        <div>
          <div style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace",marginBottom:4}}>LATEST TOP SIGNALS</div>
          <div style={{fontSize:16,fontWeight:900,color:t.tx}}>오늘 바로 볼 만한 핵심 카드</div>
        </div>
        <button onClick={()=>setFilter("top")} style={{border:`1px solid ${t.brd}`,background:"transparent",color:t.sub,borderRadius:8,padding:"7px 10px",fontSize:10,fontWeight:800,cursor:"pointer",fontFamily:"'JetBrains Mono',monospace"}}>TOP ONLY</button>
      </div>
      <div style={{display:"flex",flexDirection:"column",gap:10}}>{latestTop.map((card,i)=>(<NewsItem key={card.T.slice(0,20)+i} card={card} dark={dark}/>))}</div>
    </div>

    <div>
      <input type="text" value={search} onChange={e=>setSearch(e.target.value)} placeholder="🔍 카드 제목 · 요약 · gist 검색..."
        style={{width:"100%",padding:"10px 14px",borderRadius:10,border:`1px solid ${t.brd}`,fontSize:12,outline:"none",fontFamily:"inherit",background:t.card2,color:t.tx,boxSizing:"border-box"}}
        onFocus={e=>e.target.style.borderColor=t.cyan} onBlur={e=>e.target.style.borderColor=t.brd}/>
    </div>

    <div style={{display:"flex",gap:4,overflowX:"auto",paddingBottom:4}}>
      {[{k:"all",l:`ALL ${kb.cardCount}`},{k:"top",l:`TOP ${sigCounts.t}`},{k:"high",l:`HIGH ${sigCounts.h}`},{k:"KR",l:`🇰🇷 ${regCounts.KR||""}`},{k:"US",l:`🇺🇸 ${regCounts.US||""}`},{k:"CN",l:`🇨🇳 ${regCounts.CN||""}`},{k:"EU",l:`🇪🇺 ${regCounts.EU||""}`},{k:"JP",l:`🇯🇵 ${regCounts.JP||""}`}].map(f=>(
        <button key={f.k} onClick={()=>{setFilter(f.k);setShowCount(15);}} style={{
          background:filter===f.k?t.cyan:t.card2,color:filter===f.k?"#000":t.sub,
          border:`1px solid ${filter===f.k?"transparent":t.brd}`,borderRadius:999,padding:"6px 10px",
          fontSize:10,fontWeight:700,cursor:"pointer",whiteSpace:"nowrap",fontFamily:"'JetBrains Mono',monospace",
        }}>{f.l}</button>
      ))}
    </div>

    <div style={{display:"flex",alignItems:"center",gap:8}}>
      <span style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace"}}>CARD FEED</span>
      <div style={{flex:1,height:1,background:t.brd}}/>
    </div>

    {dates.map(date=>(<div key={date} style={{marginBottom:2}}>
      <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:8}}>
        <span style={{fontSize:10,color:"#3a6090",fontFamily:"'JetBrains Mono',monospace"}}>{date}</span>
        <div style={{flex:1,height:1,background:t.brd}}/>
      </div>
      <div style={{display:"flex",flexDirection:"column",gap:10}}>
        {visible.filter(c=>c.d===date).map((card,i)=>(<NewsItem key={card.T.slice(0,20)+i} card={card} dark={dark}/>))}
      </div>
    </div>))}

    {showCount<filtered.length&&(<button onClick={()=>setShowCount(s=>s+15)} style={{
      width:"100%",padding:"10px",borderRadius:10,border:`1px solid ${t.brd}`,
      background:t.card2,color:t.sub,fontSize:10,fontWeight:700,cursor:"pointer",
      fontFamily:"'JetBrains Mono',monospace",marginTop:2,
    }}>&gt; load more ({filtered.length-showCount} remaining)</button>)}
  </div>);
}

/* ChatBot *//* ChatBot */
function ChatBot({kb,dark}){const t=T(dark);
  const fmtCards=(cards)=>{if(!cards.length)return null;let r="";cards.forEach((c,i)=>{r+=`${sigL[c.s]} ${c.T}\n`;if(c.sub)r+=`${c.sub}\n`;if(c.url)r+=`🔗 ${c.url}\n`;if(i<cards.length-1)r+="\n---\n\n";});return r;};
  const [msgs, setMsgs] = useState([
  {
    role: "assistant",
    content:
      `안녕, 강차장이야. 🔋\n\n` +
      `궁금한 주제를 편하게 보내줘.\n` +
      `핵심부터 짧게 정리해주고,\n` +
      `관련 카드나 최근 이슈도 같이 찾아줄게.`,
    tier: null
  }
]);
  const[input,setInput]=useState("");const[loading,setLoading]=useState(false);const[mode,setMode]=useState("");
  const endRef=useRef(null);useEffect(()=>{endRef.current?.scrollIntoView({behavior:"smooth"});},[msgs]);
  const tierL={faq:"💡 FAQ",cards:`📚 CARD_DB (${kb.cardCount})`,brave:"🔍 BRAVE",info:"💬 SYS"};
  const matchFaq=(q)=>{const l=q.toLowerCase();for(const f of kb.faq){if(f.k.some(k=>l.includes(k)))return f.a;}return null;};
  const searchBrave=async(q)=>{try{const r=await fetch("/api/brave",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:q+" battery ESS 2026"})});const d=await r.json();if(d.error)return null;const res=(d.web?.results||[]).slice(0,3);if(!res.length)return null;let rp="🔍 BRAVE SEARCH:\n\n";res.forEach((r,i)=>{rp+=(i+1)+". "+r.title+"\n"+(r.description||"").substring(0,100)+"...\n\n";});return rp;}catch(e){return null;}};
  const send=async()=>{const txt=input.trim();if(!txt||loading)return;setInput("");const nm=[...msgs,{role:"user",content:txt}];setMsgs(nm);setLoading(true);
    setMode("FAQ_SCAN");const fa=matchFaq(txt);if(fa){setMsgs(p=>[...p,{role:"assistant",content:fa,tier:"faq"}]);setLoading(false);return;}
    setMode(`CARD_DB(${kb.cardCount})`);const cr=searchCards(kb.cards,txt);const ca=fmtCards(cr);if(ca){setMsgs(p=>[...p,{role:"assistant",content:ca,tier:"cards"}]);setLoading(false);return;}
    if(/(최신|뉴스|소식|현황|지금|오늘|어제|이번|최근|검색|찾아|가격|시세)/.test(txt)){setMode("BRAVE_SEARCH");const br=await searchBrave(txt);if(br){setMsgs(p=>[...p,{role:"assistant",content:br,tier:"brave"}]);setLoading(false);return;}}
    setMsgs(p=>[...p,{role:"assistant",content:"음... 이건 제가 아직 모르는 내용이네요 😅\n\n이렇게 검색해보세요:\n• FEOC, LFP, 전고체, ESS 등 키워드\n• '최신 배터리 뉴스' → Brave 검색\n• 정책 → 트래커 탭에서 확인!",tier:"info"}]);setLoading(false);};
  const qQ = [
  "오늘 핵심 뉴스 3개",
  "LFP 리스크 한 번에",
  "한국 정책 일정 뭐 있어?",
  "미국 FEOC 쉽게 설명해줘",
  "이번주 ESS 시그널 요약",
  "전고체 어디까지 왔어?",
  "중국 가격 흐름 체크",
  "먼저 봐야 할 카드 추천"
];
  return(<div style={{display:"flex",flexDirection:"column",height:"calc(100vh - 190px)"}}>
    <div style={{flex:1,overflowY:"auto",padding:"12px 14px 8px"}}>
      {msgs.length<=1&&<div style={{display:"flex",flexWrap:"wrap",gap:5,marginTop:6}}>{qQ.map(q=>(<button key={q} onClick={()=>setInput(q)} style={{background:t.card2,border:`1px solid ${t.brd}`,borderRadius:4,padding:"6px 12px",fontSize:11,color:t.cyan,cursor:"pointer",fontFamily:"'JetBrains Mono',monospace"}}>{q}</button>))}</div>}
      {msgs.map((m,i)=>(<div key={i} style={{display:"flex",justifyContent:m.role==="user"?"flex-end":"flex-start",marginBottom:10}}>
        {m.role==="assistant"&&<img src="/data/kang.png" alt="강차장" style={{width:28,height:28,borderRadius:14,marginRight:7,flexShrink:0,marginTop:2,border:"2px solid #2a1a40"}}/>}
        <div style={{maxWidth:"82%"}}><div style={{padding:"10px 12px",fontSize:12,lineHeight:1.55,whiteSpace:"pre-wrap",wordBreak:"break-word",borderRadius:m.role==="user"?"10px 10px 2px 10px":"10px 10px 10px 2px",background:m.role==="user"?"#388BFD":t.card2,color:m.role==="user"?"#fff":t.tx,border:m.role==="user"?"none":`1px solid ${t.brd}`,fontFamily:m.role==="assistant"?"'JetBrains Mono','Pretendard',monospace":"inherit"}}>{m.content}</div>
        {m.tier&&<span style={{fontSize:8,color:t.sub,marginTop:2,display:"block",paddingLeft:3,fontFamily:"'JetBrains Mono',monospace"}}>{tierL[m.tier]}</span>}</div>
      </div>))}
      {loading&&<div style={{display:"flex",gap:7,marginBottom:10}}><img src="/data/kang.png" alt="강차장" style={{width:28,height:28,borderRadius:14,flexShrink:0,border:"2px solid #2a1a40"}}/><div style={{background:t.card2,padding:"10px 12px",borderRadius:"10px 10px 10px 2px",border:`1px solid ${t.brd}`}}><div style={{display:"flex",alignItems:"center",gap:5}}><div style={{display:"flex",gap:2}}>{[0,1,2].map(i=>(<div key={i} style={{width:5,height:5,borderRadius:2,background:t.cyan,animation:"pulse 1s ease "+(i*0.2)+"s infinite"}}/>))}</div><span style={{fontSize:9,color:t.cyan,fontFamily:"'JetBrains Mono',monospace"}}>{mode}...</span></div></div></div>}
      <div ref={endRef}/></div>
    <div style={{padding:"8px 12px 14px",background:"#0A0E14",borderTop:`1px solid ${t.brd}`}}><div style={{display:"flex",gap:6}}><input type="text" value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==="Enter"&&send()} placeholder="질문을 입력하세요..." style={{flex:1,padding:"10px 14px",borderRadius:6,border:`1px solid ${t.brd}`,fontSize:13,outline:"none",fontFamily:"'JetBrains Mono',monospace",background:t.bg,color:t.tx}} onFocus={e=>e.target.style.borderColor=t.cyan} onBlur={e=>e.target.style.borderColor=t.brd}/><button onClick={send} disabled={loading||!input.trim()} style={{padding:"0 14px",borderRadius:6,border:"none",background:input.trim()&&!loading?t.cyan:"#333",color:"#000",fontSize:11,fontWeight:800,cursor:input.trim()&&!loading?"pointer":"default",fontFamily:"'JetBrains Mono',monospace"}}>GO</button></div></div>
  </div>);}

/* Tracker */
function Tracker({tracker,dark}){const t=T(dark),d=tracker;const updatedLabel=fmtDate(d.meta.lastUpdated);return(<div style={{padding:"0 14px 110px",display:"flex",flexDirection:"column",gap:12}}>
  <div style={{background:t.card2,borderRadius:10,padding:"14px",border:`1px solid ${t.brd}`}}>
    <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",gap:10,marginBottom:10}}>
      <div>
        <div style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace"}}>STATUS</div>
        <div style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace",marginTop:4}}>UPDATED {updatedLabel}</div>
      </div>
      <span style={{background:t.brd,borderRadius:4,padding:"3px 10px",fontSize:12,fontWeight:800,color:t.tx,fontFamily:"'JetBrains Mono',monospace"}}>{d.meta.totalItems}</span>
    </div>
    <div style={{display:"flex",gap:5}}>{Object.entries(d.summary).map(([s,n])=>(<div key={s} style={{flex:1,background:t.bg,borderRadius:6,padding:"8px 6px",textAlign:"center"}}><div style={{fontSize:16,fontWeight:800,color:SC[s],fontFamily:"'JetBrains Mono',monospace"}}>{n}</div><div style={{fontSize:8,color:t.sub,fontFamily:"'JetBrains Mono',monospace",marginTop:2}}>{SL[s]}</div><div style={{height:3,borderRadius:2,background:t.brd,marginTop:4}}><div style={{height:3,borderRadius:2,background:SC[s],width:pct(n,d.meta.totalItems)}}/></div></div>))}</div>
  </div>
  <div><div style={{display:"flex",alignItems:"center",gap:8,marginBottom:8}}><span style={{fontSize:10,color:"#3a6090",fontFamily:"'JetBrains Mono',monospace"}}>REGIONS</span><div style={{flex:1,height:1,background:t.brd}}/></div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:6}}>{d.regions.map(r=>(<div key={r.code} style={{background:t.card2,borderRadius:8,padding:"10px 12px",border:`1px solid ${t.brd}`}}><div style={{display:"flex",justifyContent:"space-between"}}><span style={{fontSize:13,fontWeight:700,color:t.tx}}>{r.flag} {r.name}</span><span style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace"}}>{r.total}</span></div><div style={{marginTop:6,display:"flex",alignItems:"center",gap:6}}><span style={{fontSize:8,fontWeight:700,color:SC.ACTIVE,background:SC.ACTIVE+"18",padding:"2px 6px",borderRadius:3,fontFamily:"'JetBrains Mono',monospace"}}>ACT:{r.ACTIVE}</span><div style={{flex:1,height:3,borderRadius:2,background:t.brd}}><div style={{height:3,borderRadius:2,background:SC.ACTIVE,width:pct(r.ACTIVE,r.total)}}/></div></div></div>))}</div></div>
  <div><div style={{display:"flex",alignItems:"center",gap:8,marginBottom:8}}><span style={{fontSize:10,color:"#3a6090",fontFamily:"'JetBrains Mono',monospace"}}>SCHEDULE</span><div style={{flex:1,height:1,background:t.brd}}/></div>
    <div style={{background:t.card2,borderRadius:8,padding:"4px 0",border:`1px solid ${t.brd}`}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",padding:"8px 12px 6px",borderBottom:`1px solid ${t.brd}`}}>
        <span style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace"}}>UPCOMING EVENTS</span>
        <span style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace"}}>UPDATED {updatedLabel}</span>
      </div>
      {d.upcoming.map((ev,i)=>(<div key={i} style={{padding:"8px 12px",display:"flex",alignItems:"center",gap:8,borderTop:i>0?`1px solid ${t.brd}`:"none"}}><span style={{width:36,fontSize:10,fontWeight:700,color:t.sub,fontFamily:"'JetBrains Mono',monospace",flexShrink:0}}>{ev.date}</span><div style={{width:5,height:5,borderRadius:3,background:SC.ACTIVE,flexShrink:0}}/><span style={{flex:1,fontSize:11,fontWeight:600,color:t.tx}}>{ev.title}</span><span style={{fontSize:9,color:t.sub,background:t.bg,padding:"2px 5px",borderRadius:3,fontFamily:"'JetBrains Mono',monospace",flexShrink:0}}>{ev.region}</span></div>))}
    </div></div>
</div>);}

function SmallActionPill({label,dark}){const t=T(dark);return(<span style={{fontSize:9,fontWeight:800,color:t.cyan,background:dark?"rgba(88,166,255,0.14)":"rgba(45,90,142,0.10)",padding:"4px 8px",borderRadius:999,fontFamily:"'JetBrains Mono',monospace",letterSpacing:0.4}}>{label}</span>);}

function SeriesActionButton({label,onClick,primary=false,dark}){const t=T(dark);return(<button onClick={onClick} style={{flex:1,border:primary?"none":`1px solid ${t.brd}`,borderRadius:10,padding:"10px 12px",background:primary?t.cyan:"transparent",color:primary?"#000":t.tx,fontSize:11,fontWeight:900,cursor:"pointer",fontFamily:"'JetBrains Mono',monospace"}}>{label}</button>);}

function EpisodeCard({item,dark}){const t=T(dark);const clickable=!!item.url;return(<div onClick={()=>clickable&&window.open(item.url,"_blank")} style={{background:t.card2,borderRadius:10,padding:"12px 14px",border:`1px solid ${t.brd}`,cursor:clickable?"pointer":"default"}}>
  <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",gap:10}}>
    <div style={{flex:1,minWidth:0}}>
      <div style={{display:"flex",alignItems:"center",gap:6,marginBottom:6,flexWrap:"wrap"}}>
        <span style={{fontSize:10,color:t.sub}}>🎨 웹툰</span>
        {item.tag&&<SmallActionPill label={item.tag} dark={dark}/>}
        {item.isNew&&<span style={{fontSize:8,fontWeight:800,color:"#000",background:t.cyan,padding:"2px 6px",borderRadius:3,fontFamily:"'JetBrains Mono',monospace"}}>NEW</span>}
      </div>
      <h3 style={{fontSize:14,fontWeight:800,color:t.tx,margin:"0 0 4px",lineHeight:1.35}}>{item.title}</h3>
      <p style={{fontSize:11,color:t.sub,margin:0,lineHeight:1.5}}>{item.subtitle}</p>
      <div style={{display:"flex",gap:10,fontSize:10,color:t.sub,marginTop:8,fontFamily:"'JetBrains Mono',monospace"}}><span>{item.date}</span>{clickable&&<span>OPEN ↗</span>}</div>
    </div>
  </div>
</div>);}

function CollectionFolder({collection,dark,defaultOpen=false}){const t=T(dark);const[open,setOpen]=useState(defaultOpen);return(<div style={{background:t.card2,borderRadius:16,border:`1px solid ${t.brd}`,overflow:"hidden",boxShadow:t.sh}}>
  <div style={{height:4,background:`linear-gradient(90deg,${collection.color},${collection.color}66)`}}/>
  <div style={{padding:"16px"}}>
    <div style={{display:"flex",alignItems:"flex-start",justifyContent:"space-between",gap:12}}>
      <div style={{display:"flex",gap:12,flex:1,minWidth:0}}>
        <div style={{width:52,height:52,borderRadius:14,background:dark?"rgba(248,81,73,0.12)":"rgba(248,81,73,0.08)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:24,flexShrink:0}}>📁</div>
        <div style={{flex:1,minWidth:0}}>
          <div style={{display:"flex",alignItems:"center",gap:8,flexWrap:"wrap",marginBottom:6}}>
            <SmallActionPill label={collection.badge||"SERIES"} dark={dark}/>
            <span style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace"}}>{collection.items.length} EPISODES</span>
            <span style={{fontSize:10,color:"#F85149",fontFamily:"'JetBrains Mono',monospace"}}>{collection.status}</span>
          </div>
          <h3 style={{fontSize:20,fontWeight:900,color:t.tx,margin:"0 0 6px",lineHeight:1.28}}>{collection.title}</h3>
          <p style={{fontSize:12,color:t.sub,margin:0,lineHeight:1.58}}>{collection.subtitle}</p>
          <p style={{fontSize:11,color:t.sub,opacity:0.95,margin:"8px 0 0",lineHeight:1.55}}>{collection.description}</p>
          <div style={{display:"flex",gap:6,flexWrap:"wrap",marginTop:10}}>
            {collection.items.map(item=><span key={item.id} style={{fontSize:9,color:t.tx,background:dark?"rgba(255,255,255,0.06)":"rgba(0,0,0,0.04)",padding:"5px 8px",borderRadius:999,fontFamily:"'JetBrains Mono',monospace"}}>{item.tag}</span>)}
          </div>
        </div>
      </div>
      <button onClick={()=>setOpen(v=>!v)} style={{border:"none",background:"transparent",color:t.sub,cursor:"pointer",fontSize:18,paddingTop:6,transform:open?"rotate(90deg)":"rotate(0deg)",transition:"transform 180ms ease"}}>›</button>
    </div>
    <div style={{display:"flex",gap:8,marginTop:14}}>
      <SeriesActionButton label="시리즈 소개 보기 ↗" onClick={()=>window.open(collection.landingUrl,"_blank")} primary dark={dark}/>
      <SeriesActionButton label="EP.1 시작 ↗" onClick={()=>window.open(collection.items[0].url,"_blank")} dark={dark}/>
    </div>
  </div>
  {open&&<div style={{padding:"0 16px 16px",display:"flex",flexDirection:"column",gap:10}}>
    <div style={{height:1,background:t.brd,marginBottom:2}}/>
    {collection.items.map(item=><EpisodeCard key={item.id} item={item} dark={dark}/>)}
  </div>}
</div>);}

function LegacyShelf({items,dark}){const t=T(dark);const[open,setOpen]=useState(false);return(<div style={{background:t.card2,borderRadius:12,border:`1px solid ${t.brd}`,overflow:"hidden"}}>
  <button onClick={()=>setOpen(v=>!v)} style={{width:"100%",textAlign:"left",background:"transparent",border:"none",padding:"14px 16px",cursor:"pointer",color:t.tx,display:"flex",justifyContent:"space-between",alignItems:"center",gap:12}}>
    <div>
      <div style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace",marginBottom:4}}>LEGACY / STANDALONE</div>
      <div style={{fontSize:15,fontWeight:800}}>기존 웹툰 아카이브</div>
      <div style={{fontSize:11,color:t.sub,marginTop:4}}>독립 공개본과 이전 회차를 별도로 모아둔 아카이브입니다.</div>
    </div>
    <div style={{fontSize:18,color:t.sub,transform:open?"rotate(90deg)":"rotate(0deg)",transition:"transform 180ms ease"}}>›</div>
  </button>
  {open&&<div style={{padding:"0 14px 14px",display:"flex",flexDirection:"column",gap:8}}>{items.map(item=><ContentCard key={item.id} item={{...item,category:"webtoon"}} category="webtoon" dark={dark}/>)}</div>}
</div>);}

function WebtoonHero({collection,dark}){const t=T(dark);return(<div style={{background:`linear-gradient(135deg, ${dark?"#151B2B":"#ffffff"}, ${dark?"#232D47":"#EEF3FF"})`,borderRadius:16,padding:"16px",border:`1px solid ${dark?"#2C3550":t.brd}`}}>
  <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",gap:14}}>
    <div style={{flex:1,minWidth:0}}>
      <div style={{display:"flex",alignItems:"center",gap:8,flexWrap:"wrap",marginBottom:8}}>
        <SmallActionPill label="FEATURED SERIES" dark={dark}/>
        <span style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace"}}>{collection.status}</span>
      </div>
      <h2 style={{fontSize:22,fontWeight:900,color:t.tx,margin:"0 0 6px",lineHeight:1.25}}>{collection.title}</h2>
      <p style={{fontSize:12,color:t.sub,margin:0,lineHeight:1.62}}>{collection.hook}</p>
      <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:8,marginTop:12}}>
        {collection.items.map((item,idx)=><div key={item.id} style={{background:dark?"rgba(10,14,20,0.65)":"rgba(255,255,255,0.88)",border:`1px solid ${t.brd}`,borderRadius:12,padding:"10px 9px"}}><div style={{fontSize:9,color:item.color,fontFamily:"'JetBrains Mono',monospace",fontWeight:800}}>STEP {idx+1}</div><div style={{fontSize:11,color:t.tx,fontWeight:800,lineHeight:1.35,marginTop:5}}>{item.tag}</div><div style={{fontSize:9,color:t.sub,lineHeight:1.45,marginTop:4}}>{item.title.replace(/^([A-Z]+\.)?\d+\s*/,'')}</div></div>)}
      </div>
    </div>
    <div style={{width:62,height:62,borderRadius:18,background:dark?"rgba(248,81,73,0.12)":"rgba(248,81,73,0.08)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:32,flexShrink:0}}>🎬</div>
  </div>
  <div style={{display:"flex",gap:8,marginTop:14}}>
    <SeriesActionButton label="시리즈 소개 보기 ↗" onClick={()=>window.open(collection.landingUrl,"_blank")} primary dark={dark}/>
    <SeriesActionButton label="EP.1 시작 ↗" onClick={()=>window.open(collection.items[0].url,"_blank")} dark={dark}/>
  </div>
</div>);}

function WebtoonLibrary({dark}){const t=T(dark);const featured=WEBTOON_COLLECTIONS[0];return(<div style={{padding:"10px 14px 110px",display:"flex",flexDirection:"column",gap:12}}>
  <WebtoonHero collection={featured} dark={dark}/>
  <div style={{background:t.card2,borderRadius:12,padding:"14px 16px",border:`1px solid ${t.brd}`}}>
    <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",gap:8,marginBottom:6}}>
      <div>
        <div style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace",marginBottom:4}}>WEBTOON LIBRARY</div>
        <h2 style={{fontSize:18,fontWeight:900,color:t.tx,margin:0}}>웹툰 라이브러리</h2>
      </div>
      <div style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace"}}>{WEBTOON_COLLECTIONS.length} COLLECTION</div>
    </div>
    <p style={{fontSize:12,color:t.sub,lineHeight:1.6,margin:0}}>공개된 웹툰을 시리즈 단위로 정리한 아카이브입니다. 같은 주제의 회차를 한곳에서 순서대로 확인할 수 있습니다.</p>
  </div>
  {WEBTOON_COLLECTIONS.map((collection,idx)=><CollectionFolder key={collection.id} collection={collection} dark={dark} defaultOpen={idx===0}/>) }
</div>);}


function NewsDesk({kb,dark}){const t=T(dark);const[filter,setFilter]=useState("all");const[search,setSearch]=useState("");const[showCount,setShowCount]=useState(60);const regions=["all","top","high","KR","US","CN","EU","JP","GL"];let filtered=kb.cards;if(filter==="top")filtered=filtered.filter(c=>c.s==="t");else if(filter==="high")filtered=filtered.filter(c=>c.s==="h");else if(filter!=="all")filtered=filtered.filter(c=>c.r===filter);if(search){const sw=search.toLowerCase().trim();filtered=filtered.filter(c=>c.T.toLowerCase().includes(sw)||(c.sub||"").toLowerCase().includes(sw)||(c.g||"").toLowerCase().includes(sw)||(c.src||"").toLowerCase().includes(sw)||(c.k||[]).some(k=>String(k).toLowerCase().includes(sw)));}const ordered=[...filtered].sort((a,b)=>{if(a.d!==b.d)return String(b.d).localeCompare(String(a.d));const sigOrder={t:3,h:2,m:1,i:0};if((sigOrder[b.s]||0)!==(sigOrder[a.s]||0))return (sigOrder[b.s]||0)-(sigOrder[a.s]||0);return String(a.T).localeCompare(String(b.T));});const visible=ordered.slice(0,showCount);const groupedMap=visible.reduce((acc,card)=>{(acc[card.d]||(acc[card.d]=[])).push(card);return acc;},{});const grouped=Object.entries(groupedMap).sort((a,b)=>b[0].localeCompare(a[0]));const latestDate=ordered[0]?.d||"-";const latestTop=ordered.filter(c=>c.s==="t"||c.s==="h").slice(0,4);const filterCount=ordered.length;const topCount=ordered.filter(c=>c.s==="t").length;const highCount=ordered.filter(c=>c.s==="h").length;const formatDateLabel=(date)=>{if(!date)return"DATE UNKNOWN";const[yy,mm,dd]=String(date).split("-");return `${yy}.${mm}.${dd}`;};const formatDateSub=(date)=>{const today=latestDate;const ds=[...new Set(ordered.map(c=>c.d))].sort((a,b)=>b.localeCompare(a));const idx=ds.indexOf(date);if(date===today)return"LATEST";if(idx===1)return"PREVIOUS";return `${(groupedMap[date]||[]).length} CARDS`;};return(<div style={{padding:"10px 14px 110px",display:"flex",flexDirection:"column",gap:12}}><div style={{background:t.card2,borderRadius:16,padding:"16px",border:`1px solid ${t.brd}`}}><div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",gap:12}}><div style={{flex:1,minWidth:0}}><div style={{display:"flex",alignItems:"center",gap:8,flexWrap:"wrap",marginBottom:8}}><SmallActionPill label="NEWS DESK" dark={dark}/><span style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace"}}>UPDATED {latestDate!=="-"?formatDateLabel(latestDate):"-"}</span></div><h2 style={{fontSize:22,fontWeight:900,color:t.tx,margin:"0 0 6px",lineHeight:1.25}}>날짜별로 정리한 뉴스 카드 피드</h2><p style={{fontSize:12,color:t.sub,margin:0,lineHeight:1.6}}>최신 날짜가 위로 오고, 같은 날짜 안에서는 TOP/HIGH 시그널이 먼저 보이도록 정리했습니다. 지역 필터와 검색으로 바로 좁혀볼 수 있습니다.</p></div><div style={{width:58,height:58,borderRadius:16,background:dark?"rgba(88,166,255,0.12)":"rgba(88,166,255,0.08)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:28,flexShrink:0}}>📰</div></div><div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:8,marginTop:14}}>{[{label:"VISIBLE",value:visible.length},{label:"TOTAL",value:filterCount},{label:"TOP",value:topCount},{label:"HIGH",value:highCount}].map(item=>(<div key={item.label} style={{background:t.bg,border:`1px solid ${t.brd}`,borderRadius:12,padding:"10px 8px",textAlign:"center"}}><div style={{fontSize:15,fontWeight:900,color:t.tx,fontFamily:"'JetBrains Mono',monospace"}}>{item.value}</div><div style={{fontSize:9,color:t.sub,fontFamily:"'JetBrains Mono',monospace",marginTop:4}}>{item.label}</div></div>))}</div><div style={{marginTop:14,display:"flex",gap:6,overflowX:"auto",paddingBottom:2}}>{regions.map(r=>{const active=filter===r;const label=r==="all"?"ALL":r==="top"?"TOP":r==="high"?"HIGH":r;return(<button key={r} onClick={()=>{setFilter(r);setShowCount(60);}} style={{border:active?"none":`1px solid ${t.brd}`,background:active?t.cyan:"transparent",color:active?"#000":t.tx,borderRadius:999,padding:"7px 10px",fontSize:10,fontWeight:800,whiteSpace:"nowrap",cursor:"pointer",fontFamily:"'JetBrains Mono',monospace"}}>{label}</button>);})}</div><div style={{marginTop:10}}><input value={search} onChange={e=>{setSearch(e.target.value);setShowCount(60);}} placeholder="카드 제목 · 요약 · gist · 출처 검색" style={{width:"100%",padding:"11px 12px",borderRadius:10,border:`1px solid ${t.brd}`,background:t.bg,color:t.tx,fontSize:12,outline:"none",fontFamily:"'JetBrains Mono',monospace"}}/></div></div>{latestTop.length>0&&<div style={{background:t.card2,borderRadius:14,padding:"14px 16px",border:`1px solid ${t.brd}`}}><div style={{display:"flex",alignItems:"center",justifyContent:"space-between",gap:8,marginBottom:10}}><div><div style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace",marginBottom:4}}>HIGHLIGHTS</div><h3 style={{fontSize:18,fontWeight:900,color:t.tx,margin:0}}>먼저 볼 카드</h3></div><div style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace"}}>{latestTop.length} PICKS</div></div><div style={{display:"flex",flexDirection:"column",gap:8}}>{latestTop.map((card,idx)=><NewsItem key={`${card.d}-${idx}-highlight`} card={card} dark={dark}/>)}</div></div>}{visible.length===0?<div style={{background:t.card2,borderRadius:12,padding:"18px 16px",border:`1px solid ${t.brd}`,color:t.sub,fontSize:12,lineHeight:1.6}}>조건에 맞는 카드가 없습니다.</div>:grouped.map(([date,items])=><section key={date} style={{display:"flex",flexDirection:"column",gap:8}}><div style={{display:"flex",alignItems:"center",gap:8}}><div style={{display:"flex",alignItems:"center",gap:8,flexShrink:0}}><span style={{fontSize:11,color:t.tx,fontWeight:800,fontFamily:"'JetBrains Mono',monospace"}}>{formatDateLabel(date)}</span><span style={{fontSize:9,color:t.sub,background:t.card2,border:`1px solid ${t.brd}`,padding:"2px 6px",borderRadius:999,fontFamily:"'JetBrains Mono',monospace"}}>{formatDateSub(date)}</span><span style={{fontSize:9,color:t.sub,fontFamily:"'JetBrains Mono',monospace"}}>{items.length} cards</span></div><div style={{flex:1,height:1,background:t.brd}}/></div><div style={{display:"flex",flexDirection:"column",gap:8}}>{items.map((card,idx)=><NewsItem key={`${date}-${idx}`} card={card} dark={dark}/>)}</div></section>)}{filterCount>showCount&&<button onClick={()=>setShowCount(v=>v+30)} style={{border:`1px solid ${t.brd}`,background:t.card2,color:t.tx,borderRadius:12,padding:"12px 14px",fontSize:11,fontWeight:900,cursor:"pointer",fontFamily:"'JetBrains Mono',monospace"}}>LOAD MORE +30</button>}</div>);}

function NewsletterArchive({items,dark}){const t=T(dark);return(<div style={{padding:"10px 14px 110px",display:"flex",flexDirection:"column",gap:12}}><div style={{background:`linear-gradient(135deg, ${dark?"#151B2B":"#ffffff"}, ${dark?"#232D47":"#EEF3FF"})`,borderRadius:16,padding:"16px",border:`1px solid ${dark?"#2C3550":t.brd}`}}><div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",gap:14}}><div style={{flex:1,minWidth:0}}><div style={{display:"flex",alignItems:"center",gap:8,flexWrap:"wrap",marginBottom:8}}><SmallActionPill label="NEWSLETTER ARCHIVE" dark={dark}/><span style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace"}}>{items.length} ISSUES</span></div><h2 style={{fontSize:22,fontWeight:900,color:t.tx,margin:"0 0 6px",lineHeight:1.25}}>뉴스레터 아카이브</h2><p style={{fontSize:12,color:t.sub,margin:0,lineHeight:1.6}}>발행본이 준비되면 이 공간에 호별 아카이브가 쌓입니다. 뉴스 카드 피드와는 분리해, 발행본만 별도로 탐색할 수 있게 구성했습니다.</p></div><div style={{width:58,height:58,borderRadius:16,background:dark?"rgba(248,81,73,0.12)":"rgba(248,81,73,0.08)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:28,flexShrink:0}}>📨</div></div></div>{items.length?items.map((item,i)=><ContentCard key={i} item={{...item,category:"newsletter"}} category="newsletter" dark={dark}/>):<div style={{background:t.card2,borderRadius:14,padding:"22px 18px",border:`1px solid ${t.brd}`}}><div style={{fontSize:10,color:t.sub,fontFamily:"'JetBrains Mono',monospace",marginBottom:8}}>ARCHIVE STATUS</div><div style={{fontSize:18,fontWeight:900,color:t.tx,marginBottom:8}}>아직 공개된 발행본이 없습니다.</div><div style={{fontSize:12,color:t.sub,lineHeight:1.65}}>뉴스 카드와 웹툰, 정책 트래커를 먼저 운영하고, 뉴스레터 발행본은 준비되는 순서대로 이 탭에 별도 적재하면 됩니다.</div></div>}</div>);}

/* Content Card *//* Content Card */
function ContentCard({item,category,dark}){const t=T(dark);const clickable=!!item.url;return(<div onClick={()=>clickable&&window.open(item.url,"_blank")} style={{background:t.card2,borderRadius:10,overflow:"hidden",border:`1px solid ${t.brd}`,cursor:clickable?"pointer":"default"}}>
  <div style={{height:3,background:`linear-gradient(90deg,${item.color},${item.color}66)`}}/>
  <div style={{padding:"12px 14px"}}><div style={{display:"flex",justifyContent:"space-between",marginBottom:4}}><span style={{fontSize:10,color:t.sub}}>{CM[category]?.emoji} {CM[category]?.label}</span>{item.isNew&&<span style={{fontSize:8,fontWeight:800,color:"#000",background:t.cyan,padding:"2px 6px",borderRadius:3,fontFamily:"'JetBrains Mono',monospace"}}>NEW</span>}</div><h3 style={{fontSize:14,fontWeight:700,color:t.tx,margin:"0 0 2px",lineHeight:1.35}}>{item.title}</h3><p style={{fontSize:11,color:t.sub,margin:0,lineHeight:1.45}}>{item.subtitle}</p><div style={{display:"flex",gap:10,fontSize:10,color:t.sub,marginTop:6,fontFamily:"'JetBrains Mono',monospace"}}>{typeof item.likes!=="undefined"&&<span>👍 {item.likes}</span>}<span>{item.date}</span>{clickable&&<span>OPEN ↗</span>}</div></div>
</div>);}

/* Main */
export default function App(){
  const[tab,setTab]=useState("all");const[dark,setDark]=useState(true);
  const kb=useKnowledgeBase();const {tracker,loading:trackerLoading}=useTrackerData();const t=T(dark);
  const latestCardDateForUi=useMemo(()=>{const ds=(kb.cards||[]).map(c=>c?.d).filter(Boolean).sort((a,b)=>String(b).localeCompare(String(a)));return ds[0]||"-";},[kb.cards]);
  if(kb.loading||trackerLoading)return(<div style={{display:"flex",alignItems:"center",justifyContent:"center",minHeight:"100vh",background:t.bg,fontFamily:"'JetBrains Mono',monospace"}}><div style={{textAlign:"center"}}><div style={{fontSize:36,marginBottom:8}}>🔋</div><p style={{color:t.cyan,fontSize:11}}>LOADING INTELLIGENCE...</p><div style={{display:"flex",gap:3,justifyContent:"center",marginTop:8}}>{[0,1,2].map(i=>(<div key={i} style={{width:6,height:6,borderRadius:2,background:t.cyan,animation:"pulse 1s ease "+(i*0.2)+"s infinite"}}/>))}</div></div></div>);
  return(<div style={{maxWidth:480,margin:"0 auto",background:t.bg,minHeight:"100vh",fontFamily:"'Pretendard',-apple-system,sans-serif",position:"relative"}}>
    <style dangerouslySetInnerHTML={{__html:`@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}*{margin:0;padding:0;box-sizing:border-box}body{margin:0;background:${t.bg}}`}}/>
    {/* Header */}
    <div style={{background:"#161B26",padding:"14px 16px 16px",position:"relative",borderBottom:`1px solid ${dark?"#21293A":"#21293A"}`}}>
      <div style={{position:"absolute",top:0,left:0,right:0,height:2,background:`linear-gradient(90deg,#58A6FF,#BC8CFF,#58A6FF)`}}/>
      <div style={{display:"flex",alignItems:"center",justifyContent:"space-between"}}>
        <div style={{display:"flex",alignItems:"center",gap:10}}>
          <img src="/data/logo_light.png" alt="SBTL" style={{height:32,objectFit:"contain"}} onError={e=>{e.target.style.display="none"}}/>
          <div style={{display:"flex",alignItems:"center",gap:4,background:"#0B2A0B",borderRadius:4,padding:"2px 7px"}}><div style={{width:5,height:5,borderRadius:3,background:"#3FB950",animation:"pulse 2s ease infinite"}}/><span style={{fontSize:8,color:"#3FB950",fontWeight:700,fontFamily:"'JetBrains Mono',monospace"}}>LIVE</span></div>
        </div>
        <div style={{display:"flex",alignItems:"center",gap:8}}>
          <span style={{fontSize:10,color:"#7D8590",fontFamily:"'JetBrains Mono',monospace"}}>{kb.cardCount}</span>
          <button onClick={()=>setDark(!dark)} style={{background:"#21293A",border:"none",borderRadius:8,width:32,height:32,display:"flex",alignItems:"center",justifyContent:"center",cursor:"pointer",fontSize:14}}>{dark?"☀️":"🌙"}</button>
        </div>
      </div>
      <div style={{marginTop:10}}>
        {tab!=="all"&&<h1 style={{color:"#E6EDF3",fontSize:18,fontWeight:800,margin:0}}>{{news:"날짜별 뉴스 피드",tracker:"Policy Tracker",chatbot:"강차장의 배터리 상담소",webtoon:"LFP 웹툰 시리즈"}[tab]}</h1>}
        <p style={{color:"#7D8590",fontSize:10,margin:"2px 0 0",fontFamily:"'JetBrains Mono',monospace"}}>{{news:`Cards ${kb.cardCount} · updated ${fmtDate(latestCardDateForUi)} · live feed`,tracker:`5 regions · ${tracker.meta.totalItems} items · updated ${fmtDate(tracker.meta.lastUpdated)}`,chatbot:`배터리·ESS 이슈를 빠르게 찾고 정리해주는 AI 데스크`,webtoon:`EP.1 · EP.2 now live`}[tab]||"Battery · ESS · EV Intelligence"}</p>
      </div>
    </div>
    {/* Content */}
    {tab==="all"?<div style={{paddingTop:10}}><Home onNav={setTab} kb={kb} tracker={tracker} dark={dark}/></div>
     :tab==="news"?<NewsDesk kb={kb} dark={dark}/>
     :tab==="chatbot"?<ChatBot kb={kb} dark={dark}/>
     :tab==="tracker"?<div style={{paddingTop:10}}><Tracker tracker={tracker} dark={dark}/></div>
     :tab==="webtoon"?<WebtoonLibrary dark={dark}/>
     :null}
    {/* Tab Bar */}
    <div style={{position:"fixed",bottom:0,left:"50%",transform:"translateX(-50%)",width:"100%",maxWidth:480,background:dark?t.card:"#fff",borderTop:`1px solid ${t.brd}`,display:"flex",padding:"6px 4px 14px",zIndex:100}}>
      {CATS.map(cat=>{const isA=tab===cat.key;
        return(<button key={cat.key} onClick={()=>setTab(cat.key)} style={{display:"flex",flexDirection:"column",alignItems:"center",gap:2,padding:"4px 0",cursor:"pointer",border:"none",background:"none",flex:1,minWidth:0,position:"relative"}}>
          {isA&&<div style={{position:"absolute",top:0,left:"50%",transform:"translateX(-50%)",width:20,height:2,borderRadius:1,background:t.cyan}}/>}
          <span style={{fontSize:22,lineHeight:1,filter:isA?"none":"grayscale(0.3) opacity(0.7)"}}>{cat.icon}</span>
          <span style={{fontSize:9,fontWeight:isA?700:500,color:isA?t.cyan:t.sub,fontFamily:"'JetBrains Mono',monospace"}}>{cat.label}</span>
        </button>);
      })}
    </div>
  </div>);}
