import { useState, useEffect, useRef } from "react";

const LOGO_D = "/data/logo.png";
const TD = {meta:{total:49,lastUpdated:"2026.04.03"},summary:{ACTIVE:22,UPCOMING:12,WATCH:11,DONE:4},
  regions:[{code:"NA",flag:"🇺🇸",name:"북미",total:9,ACTIVE:3},{code:"EU",flag:"🇪🇺",name:"유럽",total:13,ACTIVE:4},{code:"CN",flag:"🇨🇳",name:"중국",total:9,ACTIVE:5},{code:"KR",flag:"🇰🇷",name:"한국",total:9,ACTIVE:4},{code:"JP",flag:"🇯🇵",name:"일본",total:9,ACTIVE:6}],
  upcoming:[{date:"Q2 초",title:"EU Battery Booster 공모",region:"EU"},{date:"05.04",title:"KR 배터리 정보공개 마감",region:"KR"},{date:"06.30",title:"NA §30C 세액공제 종료",region:"NA"}],
};
const CD = {
  newsletter:[{id:1,title:"CEO 뉴스레터 Vol.06",subtitle:"K-배터리 미래 전략",date:"2026.03.28",isNew:true,color:"#E63946",likes:38},{id:2,title:"Vol.05",subtitle:"글로벌 공급망 변화",date:"2026.03.21",isNew:true,color:"#457B9D",likes:64},{id:3,title:"Vol.04",subtitle:"ESG 경영",date:"2026.03.14",isNew:false,color:"#2A9D8F",likes:89}],
  webtoon:[{id:1,title:"EP.07 전고체의 시대",subtitle:"K-Battery 2026",date:"2026.03.30",isNew:true,color:"#6C5CE7",likes:45},{id:2,title:"EP.06 리사이클링 혁명",subtitle:"K-Battery 2026",date:"2026.03.23",isNew:true,color:"#A29BFE",likes:78},{id:3,title:"EP.05 글로벌 배터리 전쟁",subtitle:"K-Battery 2026",isNew:false,color:"#FD79A8",likes:134}],
};
const CATS=[{key:"all",label:"홈",icon:"🏠"},{key:"newsletter",label:"뉴스레터",icon:"📨"},{key:"webtoon",label:"웹툰",icon:"🎨"},{key:"tracker",label:"트래커",icon:"📊"},{key:"chatbot",label:"AI 챗봇",icon:"🤖"}];
const CM={newsletter:{emoji:"📨",label:"뉴스레터"},webtoon:{emoji:"🎨",label:"웹툰"}};
const SC={ACTIVE:"#E63946",UPCOMING:"#F4A261",WATCH:"#457B9D",DONE:"#95A5A6"};
const SL={ACTIVE:"진행중",UPCOMING:"예정",WATCH:"모니터링",DONE:"완료"};
const sigC={t:"#E63946",h:"#F4A261",m:"#457B9D"};
const sigL={t:"TOP",h:"HIGH",m:"MID"};
const regFlag={US:"🇺🇸",KR:"🇰🇷",EU:"🇪🇺",CN:"🇨🇳",JP:"🇯🇵",GL:"🌐","US/KR":"🇺🇸🇰🇷"};
const T=(dk)=>({bg:dk?"#0f1117":"#F8F9FC",card:dk?"#1a1f2e":"#FFFFFF",tx:dk?"#e8e8e8":"#1a1a2a",sub:dk?"#888":"#6b7280",brd:dk?"#252d3d":"#e5e7eb",sh:dk?"0 2px 8px rgba(0,0,0,0.3)":"0 2px 12px rgba(0,0,0,0.06)",hdr:dk?"linear-gradient(135deg,#1a1f2e,#0f1520)":"linear-gradient(135deg,#1e3a5f,#2d5a8e)"});

function useKnowledgeBase(){const[cards,setCards]=useState([]);const[faq,setFaq]=useState([]);const[loading,setLoading]=useState(true);
  useEffect(()=>{Promise.all([fetch("/data/cards.json").then(r=>r.json()).then(d=>d.cards||d).catch(()=>[]),fetch("/data/faq.json").then(r=>r.json()).catch(()=>[])]).then(([c,f])=>{setCards(c);setFaq(f);setLoading(false);});},[]);
  return{cards,faq,loading,cardCount:cards.length,faqCount:faq.length};}

function searchCards(cards,q){const ws=q.toLowerCase().replace(/[?!.,]/g,"").split(/\s+/).filter(w=>w.length>=2);if(!ws.length)return[];
  return cards.map(c=>{let sc=0;const tl=c.T.toLowerCase(),gl=(c.g||"").toLowerCase(),ks=c.k||[];for(const w of ws){if(tl.includes(w))sc+=10;if(gl.includes(w))sc+=5;if(ks.some(k=>k.includes(w)||w.includes(k)))sc+=8;}if(c.s==="t")sc*=2;else if(c.s==="h")sc*=1.5;return{...c,sc};}).filter(c=>c.sc>0).sort((a,b)=>b.sc-a.sc).slice(0,3);}

/* News Feed Item */
function NewsItem({card, dark}) {
  const t = T(dark);
  const sig = card.s;
  const flag = regFlag[card.r] || "🌐";
  const dateStr = card.d ? card.d.slice(5).replace("-",".") : "";
  
  const handleClick = () => {
    if (card.url) window.open(card.url, "_blank");
  };
  
  return (
    <div onClick={handleClick} style={{
      background: t.card, borderRadius: 14, padding: "12px 14px", 
      borderLeft: `3px solid ${sigC[sig]}`,
      boxShadow: t.sh, cursor: card.url ? "pointer" : "default",
      transition: "all 0.15s",
    }}>
      <div style={{display:"flex",alignItems:"center",gap:6,marginBottom:5}}>
        <span style={{fontSize:8,fontWeight:800,color:sigC[sig],background:sigC[sig]+"14",padding:"2px 6px",borderRadius:4,letterSpacing:0.5}}>{sigL[sig]}</span>
        <span style={{fontSize:10,color:t.sub}}>{flag} {dateStr}</span>
        {card.src && <span style={{fontSize:9,color:t.sub,marginLeft:"auto",opacity:0.6}}>{card.src}</span>}
      </div>
      <h3 style={{fontSize:13,fontWeight:700,color:t.tx,margin:0,lineHeight:1.4}}>{card.T}</h3>
      {card.sub && <p style={{fontSize:11,color:t.sub,margin:"4px 0 0",lineHeight:1.4}}>{card.sub}</p>}
      {card.url && <div style={{display:"flex",alignItems:"center",gap:4,marginTop:6}}>
        <span style={{fontSize:10,color:"#2d5a8e",fontWeight:600}}>원문 보기 →</span>
      </div>}
    </div>
  );
}

/* Home = News Feed */
function Home({onNav, dark, kb}) {
  const t = T(dark);
  const [filter, setFilter] = useState("all");
  const [showCount, setShowCount] = useState(15);
  
  const filtered = filter === "all" 
    ? kb.cards 
    : filter === "top" ? kb.cards.filter(c => c.s === "t")
    : filter === "high" ? kb.cards.filter(c => c.s === "h")
    : kb.cards.filter(c => c.r === filter);
  
  const visible = filtered.slice(0, showCount);
  const dates = [...new Set(visible.map(c => c.d))];
  
  return (
    <div style={{padding:"0 16px 120px"}}>
      {/* Quick Stats */}
      <div style={{display:"flex",gap:6,marginBottom:12}}>
        <div style={{flex:1,background:t.card,borderRadius:12,padding:"10px",textAlign:"center",boxShadow:t.sh,border:`1px solid ${t.brd}`}}>
          <div style={{fontSize:20,fontWeight:800,color:t.tx}}>{kb.cardCount}</div>
          <div style={{fontSize:9,color:t.sub}}>인사이트</div>
        </div>
        {TD.regions.slice(0,4).map(r=>(
          <div key={r.code} style={{flex:1,background:t.card,borderRadius:12,padding:"10px 0",textAlign:"center",boxShadow:t.sh,border:`1px solid ${t.brd}`}}>
            <div style={{fontSize:13}}>{r.flag}</div>
            <div style={{fontSize:13,fontWeight:800,color:t.tx}}>{r.ACTIVE}</div>
            <div style={{fontSize:8,color:t.sub}}>ACTIVE</div>
          </div>
        ))}
      </div>

      {/* AI Button */}
      <button onClick={()=>onNav("chatbot")} style={{width:"100%",background:dark?"linear-gradient(135deg,#1a1f2e,#0f3460)":"linear-gradient(135deg,#2d5a8e,#1e3a5f)",border:"none",borderRadius:14,padding:"14px 16px",cursor:"pointer",display:"flex",alignItems:"center",gap:10,marginBottom:14,boxShadow:"0 4px 16px rgba(30,58,95,0.15)"}}>
        <span style={{fontSize:20}}>🤖</span>
        <div style={{textAlign:"left"}}><h4 style={{color:"#fff",fontSize:13,fontWeight:700,margin:0}}>AI에게 물어보기</h4><p style={{color:"rgba(255,255,255,0.45)",fontSize:10,margin:0}}>FAQ {kb.faqCount} + Cards {kb.cardCount} + Brave</p></div>
        <span style={{marginLeft:"auto",color:"rgba(255,255,255,0.3)"}}>→</span>
      </button>

      {/* Filter Chips */}
      <div style={{display:"flex",gap:5,marginBottom:12,overflowX:"auto",paddingBottom:4}}>
        {[{k:"all",l:"전체"},{k:"top",l:"🔴 TOP"},{k:"high",l:"🟠 HIGH"},{k:"KR",l:"🇰🇷"},{k:"US",l:"🇺🇸"},{k:"CN",l:"🇨🇳"},{k:"EU",l:"🇪🇺"},{k:"JP",l:"🇯🇵"}].map(f=>(
          <button key={f.k} onClick={()=>{setFilter(f.k);setShowCount(15);}} style={{
            background:filter===f.k?(dark?"#2d5a8e":"#1e3a5f"):t.card,
            color:filter===f.k?"#fff":t.sub,
            border:`1px solid ${filter===f.k?"transparent":t.brd}`,
            borderRadius:20,padding:"5px 12px",fontSize:11,fontWeight:600,
            cursor:"pointer",whiteSpace:"nowrap",fontFamily:"inherit",
          }}>{f.l}</button>
        ))}
      </div>

      {/* News Feed grouped by date */}
      {dates.map(date => (
        <div key={date} style={{marginBottom:12}}>
          <div style={{fontSize:11,fontWeight:700,color:t.sub,marginBottom:6,paddingLeft:2}}>
            {date}
          </div>
          <div style={{display:"flex",flexDirection:"column",gap:8}}>
            {visible.filter(c=>c.d===date).map((card,i) => (
              <NewsItem key={card.T.slice(0,20)+i} card={card} dark={dark}/>
            ))}
          </div>
        </div>
      ))}

      {/* Load More */}
      {showCount < filtered.length && (
        <button onClick={()=>setShowCount(s=>s+15)} style={{
          width:"100%",padding:"12px",borderRadius:12,border:`1px solid ${t.brd}`,
          background:t.card,color:t.sub,fontSize:12,fontWeight:600,cursor:"pointer",
          fontFamily:"inherit",marginTop:8,
        }}>더 보기 ({filtered.length - showCount}건 남음)</button>
      )}
    </div>
  );
}

/* ChatBot */
function ChatBot({dark,kb}){const t=T(dark);
  const fmtCards=(cards)=>{if(!cards.length)return null;let r="";cards.forEach((c,i)=>{r+=`${sigL[c.s]} ${c.T}\n`;if(c.sub)r+=`${c.sub}\n`;if(c.url)r+=`🔗 ${c.url}\n`;if(i<cards.length-1)r+="\n---\n\n";});return r;};
  const[msgs,setMsgs]=useState([{role:"assistant",content:`안녕하세요! SBTL AI 어시스턴트입니다. 🔋\n\n3단계 지식 엔진:\n💡 FAQ (${kb.faqCount}건) → 📚 카드 DB (${kb.cardCount}건) → 🔍 실시간 검색`,tier:null}]);
  const[input,setInput]=useState("");const[loading,setLoading]=useState(false);const[mode,setMode]=useState("");
  const endRef=useRef(null);useEffect(()=>{endRef.current?.scrollIntoView({behavior:"smooth"});},[msgs]);
  const tierL={faq:"💡 FAQ",cards:`📚 카드 DB (${kb.cardCount}건)`,brave:"🔍 Brave Search",info:"💬 안내"};
  const matchFaq=(q)=>{const l=q.toLowerCase();for(const f of kb.faq){if(f.k.some(k=>l.includes(k)))return f.a;}return null;};
  const searchBrave=async(q)=>{try{const r=await fetch("/api/brave",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:q+" battery ESS 2026"})});const d=await r.json();if(d.error)return null;const res=(d.web?.results||[]).slice(0,3);if(!res.length)return null;let rp="🔍 실시간 검색 결과:\n\n";res.forEach((r,i)=>{rp+=(i+1)+". "+r.title+"\n"+(r.description||"").substring(0,100)+"...\n\n";});return rp;}catch(e){return null;}};
  const send=async()=>{const txt=input.trim();if(!txt||loading)return;setInput("");const nm=[...msgs,{role:"user",content:txt}];setMsgs(nm);setLoading(true);
    setMode("FAQ");const fa=matchFaq(txt);if(fa){setMsgs(p=>[...p,{role:"assistant",content:fa,tier:"faq"}]);setLoading(false);return;}
    setMode(`카드 DB (${kb.cardCount})`);const cr=searchCards(kb.cards,txt);const ca=fmtCards(cr);if(ca){setMsgs(p=>[...p,{role:"assistant",content:ca,tier:"cards"}]);setLoading(false);return;}
    if(/(최신|뉴스|소식|현황|지금|오늘|어제|이번|최근|검색|찾아|가격|시세)/.test(txt)){setMode("Brave 검색");const br=await searchBrave(txt);if(br){setMsgs(p=>[...p,{role:"assistant",content:br,tier:"brave"}]);setLoading(false);return;}}
    setMsgs(p=>[...p,{role:"assistant",content:"이 질문에 대한 답변을 찾지 못했어요.\n\n• 더 구체적인 키워드 (예: 'FEOC', 'LFP', '전고체')\n• 최신 뉴스는 '최신 배터리 뉴스'\n• 정책 관련은 트래커 탭에서 확인",tier:"info"}]);setLoading(false);};
  const qQ=["테슬라 LFP 계약?","FEOC가 뭐야?","알루미늄 가격?","ESS 골드러시?","전고체 배터리?"];
  return(<div style={{display:"flex",flexDirection:"column",height:"calc(100vh - 200px)"}}>
    <div style={{flex:1,overflowY:"auto",padding:"14px 14px 8px"}}>
      {msgs.length<=1&&<div style={{display:"flex",flexWrap:"wrap",gap:6,marginTop:8}}>{qQ.map(q=>(<button key={q} onClick={()=>setInput(q)} style={{background:t.card,border:`1px solid ${t.brd}`,borderRadius:20,padding:"8px 14px",fontSize:12,color:t.tx,cursor:"pointer",fontFamily:"inherit",boxShadow:t.sh}}>{q}</button>))}</div>}
      {msgs.map((m,i)=>(<div key={i} style={{display:"flex",justifyContent:m.role==="user"?"flex-end":"flex-start",marginBottom:12}}>{m.role==="assistant"&&<div style={{width:28,height:28,borderRadius:14,background:"linear-gradient(135deg,#2d5a8e,#1e3a5f)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:12,marginRight:8,flexShrink:0,marginTop:2}}>🤖</div>}<div style={{maxWidth:"80%"}}><div style={{padding:"11px 14px",fontSize:13,lineHeight:1.6,whiteSpace:"pre-wrap",wordBreak:"break-word",borderRadius:m.role==="user"?"16px 16px 4px 16px":"16px 16px 16px 4px",background:m.role==="user"?"#2d5a8e":t.card,color:m.role==="user"?"#fff":t.tx,boxShadow:t.sh}}>{m.content}</div>{m.tier&&<span style={{fontSize:9,color:t.sub,marginTop:3,display:"block",paddingLeft:4,opacity:0.7}}>{tierL[m.tier]}</span>}</div></div>))}
      {loading&&<div style={{display:"flex",gap:8,marginBottom:12}}><div style={{width:28,height:28,borderRadius:14,background:"linear-gradient(135deg,#2d5a8e,#1e3a5f)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:12}}>🤖</div><div style={{background:t.card,padding:"11px 14px",borderRadius:"16px 16px 16px 4px",boxShadow:t.sh}}><div style={{display:"flex",alignItems:"center",gap:6}}><div style={{display:"flex",gap:3}}>{[0,1,2].map(i=>(<div key={i} style={{width:6,height:6,borderRadius:3,background:t.sub,animation:"pulse 1s ease "+(i*0.2)+"s infinite"}}/>))}</div><span style={{fontSize:10,color:t.sub}}>{mode}...</span></div></div></div>}
      <div ref={endRef}/></div>
    <div style={{padding:"10px 14px 16px",background:dark?"#0a0d14":"#f0f2f5",borderTop:`1px solid ${t.brd}`}}><div style={{display:"flex",gap:8}}><input type="text" value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==="Enter"&&send()} placeholder="질문을 입력하세요..." style={{flex:1,padding:"11px 16px",borderRadius:24,border:`2px solid ${t.brd}`,fontSize:14,outline:"none",fontFamily:"inherit",background:dark?"#1a1f2e":"#fff",color:t.tx}} onFocus={e=>e.target.style.borderColor="#2d5a8e"} onBlur={e=>e.target.style.borderColor=t.brd}/><button onClick={send} disabled={loading||!input.trim()} style={{width:40,height:40,borderRadius:20,border:"none",background:input.trim()&&!loading?"#2d5a8e":"#ccc",color:"#fff",fontSize:16,cursor:input.trim()&&!loading?"pointer":"default",display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0}}>↑</button></div></div>
  </div>);}

/* Tracker */
function Tracker({dark}){const t=T(dark),d=TD;return(<div style={{padding:"0 16px 120px",display:"flex",flexDirection:"column",gap:14}}>
  <div style={{background:dark?"linear-gradient(135deg,#1a1f2e,#0f3460)":"linear-gradient(135deg,#2d5a8e,#1e3a5f)",borderRadius:16,padding:"18px",color:"#fff"}}><div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:12}}><div><h2 style={{fontSize:17,fontWeight:800,margin:0}}>Policy Tracker</h2><p style={{fontSize:11,color:"rgba(255,255,255,0.5)",margin:"2px 0 0"}}>{d.meta.lastUpdated}</p></div><div style={{background:"rgba(255,255,255,0.15)",borderRadius:12,padding:"6px 14px"}}><span style={{fontSize:22,fontWeight:800}}>{d.meta.total}</span><span style={{fontSize:11,marginLeft:3,opacity:0.6}}>건</span></div></div><div style={{display:"flex",gap:6}}>{Object.entries(d.summary).map(([s,n])=>(<div key={s} style={{flex:1,background:"rgba(255,255,255,0.1)",borderRadius:10,padding:"8px 0",textAlign:"center"}}><div style={{fontSize:18,fontWeight:800}}>{n}</div><div style={{fontSize:9,fontWeight:600,color:SC[s],marginTop:2}}>{SL[s]}</div></div>))}</div></div>
  <div><h3 style={{fontSize:14,fontWeight:700,color:t.tx,margin:"0 0 8px"}}>권역별</h3><div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:8}}>{d.regions.map(r=>(<div key={r.code} style={{background:t.card,borderRadius:14,padding:"12px 14px",boxShadow:t.sh,border:`1px solid ${t.brd}`}}><span style={{fontSize:15,fontWeight:700}}>{r.flag} {r.name}</span><span style={{fontSize:12,float:"right",color:t.sub}}>{r.total}건</span><div style={{marginTop:6}}><span style={{fontSize:9,fontWeight:700,padding:"3px 8px",borderRadius:6,background:SC.ACTIVE+"12",color:SC.ACTIVE}}>ACTIVE {r.ACTIVE}</span></div></div>))}</div></div>
  <div><h3 style={{fontSize:14,fontWeight:700,color:t.tx,margin:"0 0 8px"}}>일정</h3><div style={{background:t.card,borderRadius:14,padding:"4px 0",boxShadow:t.sh,border:`1px solid ${t.brd}`}}>{d.upcoming.map((ev,i)=>(<div key={i} style={{padding:"10px 14px",display:"flex",alignItems:"center",gap:10,borderTop:i>0?`1px solid ${t.brd}`:"none"}}><span style={{width:40,fontSize:11,fontWeight:700,color:t.sub,fontFamily:"monospace",flexShrink:0}}>{ev.date}</span><div style={{width:6,height:6,borderRadius:3,background:"#E63946",flexShrink:0}}/><span style={{flex:1,fontSize:12,fontWeight:600,color:t.tx}}>{ev.title}</span><span style={{fontSize:10,color:t.sub,background:dark?"#1a2030":"#f0f2f5",padding:"2px 6px",borderRadius:4,flexShrink:0}}>{ev.region}</span></div>))}</div></div>
</div>);}

/* Content Card */
function ContentCard({item,category,dark}){const t=T(dark);return(<div style={{background:t.card,borderRadius:16,overflow:"hidden",boxShadow:t.sh,border:`1px solid ${t.brd}`}}><div style={{height:4,background:`linear-gradient(90deg,${item.color},${item.color}88)`}}/><div style={{padding:"14px 16px"}}><div style={{display:"flex",justifyContent:"space-between",marginBottom:5}}><span style={{fontSize:11,color:t.sub}}>{CM[category]?.emoji} {CM[category]?.label}</span>{item.isNew&&<span style={{fontSize:9,fontWeight:800,color:"#fff",background:"linear-gradient(135deg,#E63946,#ff6b6b)",padding:"2px 8px",borderRadius:8}}>NEW</span>}</div><h3 style={{fontSize:15,fontWeight:700,color:t.tx,margin:"0 0 3px",lineHeight:1.35}}>{item.title}</h3><p style={{fontSize:12,color:t.sub,margin:0}}>{item.subtitle}</p><div style={{display:"flex",gap:12,fontSize:11,color:t.sub,marginTop:8}}>👍 {item.likes}<span style={{marginLeft:8}}>{item.date}</span></div></div></div>);}

/* Main */
export default function App(){
  const[tab,setTab]=useState("all");const[dark,setDark]=useState(false);
  const kb=useKnowledgeBase();const t=T(dark);
  const nc=Object.keys(CD).reduce((a,c)=>a+CD[c].filter(i=>i.isNew).length,0);
  const isCT=["newsletter","webtoon"].includes(tab);const fi=isCT?CD[tab]?.map(i=>({...i,category:tab}))||[]:[];
  if(kb.loading)return(<div style={{display:"flex",alignItems:"center",justifyContent:"center",minHeight:"100vh",background:t.bg,fontFamily:"'Pretendard',sans-serif"}}><div style={{textAlign:"center"}}><div style={{fontSize:40,marginBottom:12}}>🔋</div><p style={{color:t.sub,fontSize:14}}>로딩 중...</p></div></div>);
  return(<div style={{maxWidth:480,margin:"0 auto",background:t.bg,minHeight:"100vh",fontFamily:"'Pretendard',-apple-system,sans-serif",position:"relative"}}>
    <style dangerouslySetInnerHTML={{__html:"@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}*{margin:0;padding:0;box-sizing:border-box}body{margin:0}"}}/>
    <div style={{background:t.hdr,padding:"18px 18px 22px",position:"relative"}}><div style={{display:"flex",alignItems:"center",justifyContent:"space-between"}}><div style={{display:"flex",alignItems:"center",gap:8}}><img src={LOGO_D} alt="SBTL" style={{height:28,objectFit:"contain"}} onError={e=>{e.target.style.display="none"}}/><span style={{fontSize:16,fontWeight:800,color:"#fff"}}>SBTL</span></div><button onClick={()=>setDark(!dark)} style={{background:"rgba(255,255,255,0.15)",border:"none",borderRadius:10,width:34,height:34,display:"flex",alignItems:"center",justifyContent:"center",cursor:"pointer",fontSize:15}}>{dark?"☀️":"🌙"}</button></div><div style={{marginTop:12}}><h1 style={{color:"#fff",fontSize:19,fontWeight:800,margin:0}}>{{tracker:"Policy Tracker",chatbot:"AI 챗봇"}[tab]||"콘텐츠 허브"}</h1><p style={{color:"rgba(255,255,255,0.5)",fontSize:11,margin:"2px 0 0"}}>{{tracker:"5개 권역 정책 현황",chatbot:`FAQ ${kb.faqCount} + Cards ${kb.cardCount}`}[tab]||`${kb.cardCount}건 인사이트 · 실시간 업데이트`}</p></div><div style={{position:"absolute",bottom:0,left:0,right:0,height:3,background:tab==="chatbot"?"linear-gradient(90deg,#6C5CE7,#A29BFE,#6C5CE7)":"linear-gradient(90deg,#2d5a8e,#4a90d9,#2d5a8e)"}}/></div>
    {tab==="all"?<div style={{paddingTop:12}}><Home onNav={setTab} dark={dark} kb={kb}/></div>:tab==="chatbot"?<ChatBot dark={dark} kb={kb}/>:tab==="tracker"?<div style={{paddingTop:12}}><Tracker dark={dark}/></div>:isCT?<div style={{padding:"14px 16px 120px",display:"flex",flexDirection:"column",gap:12}}>{fi.map((item,i)=>(<ContentCard key={i} item={item} category={item.category} dark={dark}/>))}</div>:null}
    <div style={{position:"fixed",bottom:0,left:"50%",transform:"translateX(-50%)",width:"100%",maxWidth:480,background:dark?"#111":"#fff",borderTop:`1px solid ${t.brd}`,display:"flex",padding:"8px 6px 16px",zIndex:100,boxShadow:"0 -4px 20px rgba(0,0,0,0.06)"}}>{CATS.map(cat=>{const isA=tab===cat.key;const cn=cat.key==="all"?0:cat.key==="chatbot"?0:cat.key==="tracker"?TD.meta.total:(CD[cat.key]?.filter(i=>i.isNew).length||0);return(<button key={cat.key} onClick={()=>setTab(cat.key)} style={{display:"flex",flexDirection:"column",alignItems:"center",gap:3,padding:"6px 0",cursor:"pointer",border:"none",background:"none",flex:1,minWidth:0,position:"relative"}}><div style={{position:"relative"}}><span style={{fontSize:20,lineHeight:1,filter:isA?"none":"grayscale(0.5) opacity(0.6)"}}>{cat.icon}</span>{cn>0&&<div style={{position:"absolute",top:-5,right:-9,background:"linear-gradient(135deg,#E63946,#ff6b6b)",color:"#fff",fontSize:8,fontWeight:800,minWidth:15,height:15,borderRadius:8,display:"flex",alignItems:"center",justifyContent:"center",padding:"0 3px",border:`2px solid ${dark?"#111":"#fff"}`}}>{cn}</div>}</div><span style={{fontSize:10,fontWeight:isA?700:500,color:isA?"#2d5a8e":t.sub}}>{cat.label}</span>{isA&&<div style={{position:"absolute",top:0,left:"50%",transform:"translateX(-50%)",width:20,height:2.5,borderRadius:2,background:"#2d5a8e"}}/>}</button>);})}</div>
  </div>);}
