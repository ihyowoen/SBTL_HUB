import { useState, useEffect, useRef } from "react";

/* Logos */
const LOGO_L = "data:image/png;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCABCAN0DASIAAhEBAxEB/8QAHQAAAQQDAQEAAAAAAAAAAAAAAAQFBgcCAwgBCf/EAEoQAAEDAwIDBAIMCA4DAAAAAAECAwQABREGEgchMRNBUWEUIggVIzJSU2JxgZGS4RYzQlVyk6LRFyQ0VGRlgpShpLHB0uJjc8L/xAAbAQEAAgMBAQAAAAAAAAAAAAAAAQQDBQYCB//EADQRAAIBAwEGAwYEBwAAAAAAAAABAgMEESEFEhMxQVEiYXEGFDOBkdE0ocHwFTJCU1SSsf/aAAwDAQACEQMRAD8A4yooooAoq3+E3sc+JvERlE6Ja0Wa1LTuRPum5lDnLlsSAVrB+EE7fOozxS4Ta94bTC1qqwvsRira1OZ90iu+G1wcgT8E4V5UBBqKKKAKKKKAKKKKAKKKKAKKKKAKKKKAKKKKAKKKKAKKKKAKknDXR9z11rKDpy2JIXIXl97blMdke/dV5AfWcAcyKjdSDQ+stR6LuTk/TtxXEceQG30YCkPIznapJ5EefUdxFAdH8c+Emnr8u2QtFtJg3K3xEQm0nmiS2gYT2hHML+Xzz0OeRHMV4sN6s8iUxc7XLiriPqjvlbR2ocBwUlXTOR411Rwg4x6WVo+6ahvCWmdRxFobTGeWEsurczsWFk8kApOQTkchzzmrV0fDgwdDyr7dHol1mX5K3ZDh2ONupXnd4pIPTHTFCD54UVbfHmx6Hsz5ctER2Jc5a97cWO7hltvdzWpJBIBOQlKSkdT0GDUlCSxrDwT4l3bTC9To0ldm7OnB7UxyXFpIJ3oa5LUjlzUBjHfXQvsYYfAbTiozmoLW63qdJB9NvWHmEL/8eAEt48VJyPhUk0nxH4lcMHWYUgvSbYnkmHOBcZ2+Dawcp5dyTjxBqzG9R8GOMaAzqKGnTeoXBgPLWlpSlfJexsc7gA4AfAVr/eZTfheH2f3Ow/gdK3pt1oOpB8pweWvWPbuSbjxF4w3mNFk8M7vb1WQ7HHEQXQ3Md55JDijtUjl0SUk5wQqoBYeO9+tC3dMcVtMG4MlPZSO0jBt4pPXe0oBDgP8AZ+ms5/Dji1wqkOXDQd4fu9rCt647KcqI+XHVkKPdlGT81Krdxr0ZrCMLFxY0oyy4klBkoZUtDau84/GNH9Ek/NXidSW9ltxl58izb2dJ0N2NONen3jpUXqufyI9qr2PXCHixEevHCm/sWG6FO9cEAljPymThbXPllPq+CTXLvFThBr/hpKKdUWJ5uHu2t3CP7rFc8MOD3pPwVbVeVdfXbgTCuDSNTcI9XodCTvabMnmhXgh5HNJ8lDPiaTwuLfEDQ7n4O8U9MrusBxJbUqQ0kOOI6HC8Ft4Y8eveqs6unD4qx5rkaqpsOncZdhU3mv6JaSX15nBlegEkADJNdM+yAsfservZzfNDSbnZdQPZUbbEiExwevuiVEJb8Pc1ED4JrmdpZbdQ4OZSoEfRVmNSM/5Xk0la0rW7XGi457+XMsiw6Pt8aMhdwaEmSRlQUfVSfADv+mnpNntCRgWuF+oT+6s7VcItyhokxXAtKhzGeaT4HwNR24aJYlzXZJuL4LiyrCkhWM+ea0O/Kc3xZtH1f3ala28HY28aifmlp3y08kg9qLT+bIX6hP7qPai0/myF+oT+6ox+AEf85O/qh++vFaAZx6tzcB82gf8AevW7S/uv6Mw8W9/wY/7x+wg11OtjazbLbBhoWk+7OoZSCD8EHH1/V41H7ZD7Yh1we5joPhfdTnqDSc61R1SUuIkx0++UkYUnzI8KQRrch1hDhcUCoZxitxbbnDW48nzvbTuXdydxDcfRdEvLv69xw9Hj/ENfYFHo8f4hr7ApH7VN/Gq+qj2qb+NV9VZzVCz0eP8AENfZFJJsBotKWynYoDOB0NZx7ehl1LgcWSO7pW2e6WYyiElRIxyHIeZoBDa4e/Dzycp/JSe/zpx9Hj/ENfYFR2tkb+Utfpj/AFoB+9Hj/ENfYFHo8f4hr7ArbUbe/Gr/AEjQDvOMaM1nsGis+9G0VaPCnTFguWiUSp1qjyH5S1h1xYJPqrIG0/k/2cZ76pSuofYxWpE3SECXMjOvW+NJPbhDal7iXThJCQTjAJPkkjqRQgqnjrZrZapdsdt8FqGuQHe2S0nalW3Zt9Uch749B31E9Iaw1BpV5RtFwdbYcOXoqlEsu/pJz15YyMHwNWV7Khh9q62Z2S8w67JD8glonA3lChyIBGc5x4EVS1ALb5c5l5u0m6T3e0kyF71nuHcAPAAYAHcAKRUUUB3drpjWdq1O1Ih2n2203IS01JjOMh9rOcK3J5lHUc+Q6daYdZcNtKjiLd9Mw9Qt2O4KUwu2RpTSlMPFxAJb7QZKDuPLOeRxzqRznLtqnWcbWnC/UjLyktsom2wP9jJSlJ9YqaX6ricHz8s1HOMy0t+yWZkJdWtJmwVjcrO3HZ8h5cq1NbEstrKz9+R9C2bxKTjTjJRkqbbSWHlOON5POvTPVZxg0WjWHFTg9MRbpnaPW1J2ojS8vRVDn+LWDlHecJI8wasiJrHgzxe7JjV1sasV7OAHXnA3uPgmQnAUMcsLA68h31UesLrNuPFd+1vSnHre7cml+jOHc3u2gZCTyHU1DNXRWoWprhFYbDbbT6kpSOgFY3UlSTS1jnGGXKdlSvpQlJcOs4qW9DTn3X79Tp/UvFzhDwgtztl0pEjXGenkqJayCCodO2kHIz1HVah4VUV5vXGPjlJYhygjTWlZKHJKFrbWzD7JrbuWp0gqcxvT37SegGDildDwY1z15Y7bMZ7eNLukdh5rcRvQt1KVJyCCMgkciDVv6p1A4/HYhaovZdjxUJbi2CzLT2LCUjCUFYy2jA5A+6rGMECpncOS1WnZaGOz2JBVcxlmfNyl4pfJfq8JdWUxrCxydN3yVZpb8aQ6wlCu1jOb21pWhK0lKu8YUKq2rr4x5/DmXmIqGfQ4fuCs5a/ijXqndz5edUuyW0uoU6hS2wQVJCtpI8M4OKtWWm8aD2m8XBy+j/Qe9N2C8XBpUuA8mKkHaHFOKRu8cYBp8GntXgY9vR/enf8AjWqPrtqOwhhmypbbQNqUiRyA+zWz+ED+qP8AM/8AWsdT3qUsqCx8i5aLYVGkoyuJb3XG+ln0wZfg/rD8+p/vLn/Gl9hs+pItyben3gPR053N9qte7l8oDFN38IH9Uf5n/rWK+ICyPUtSUnzfz/8ANY5U7qSw4r8i7Su9hUZqpGvNta85/Yl1+cabsk1bxGwMLBz35BGKrm3fyJr5q0X7UVxvCezfUltgHPZNjAJ8+80nj3HsWEt9ju2jGd33Vbs7eVGL3ubOe9o9r0tpV4ukvDFYy+ormMynHQph4ITtwRuI51p9FuP86H2j+6sfbb+j/t/dR7bf0f8Ab+6rhzptjx5yHkqckApB5jJOaXKCSkhWNuOeabDdvBj9v7qTyZ7zySjkhJ6gd9AJD15Vsjfylr9Mf61rrJpWxxK8Z2kHFCCS1G3vxq/0jTh7bf0f9v7qbVncsq6ZOaEs8rpX2Ok2NbdGRp77QfW0mR2DSh6qnFKUkFXkMlXzgDvrmqp/o3iSvTlgZtKbOmSGlKV2hkbM7lE9Np8aED/7I5x6VLs77zhcdcMha1KPNRJbyaqTs1eIqVa/1orVioSlW4RPRQ4OT2/du2+Qxjb/AI1Fu1+T/jUErB52avEV4pOOpFZdr8n/ABrAkk5NSHgnendeuMPtLmdpHebIKJMckFJ8cDmPnFT6HqR26XqNf5NxcubqHm1reU7vWoIIwCT34HfVC0ogzJUF4PRH1sr8Unr8/jVCrYxesHj/AIdVY+1Van4LqO+sYzylj16/vU6Vs8tm7cV4EuPvLUieyU7xhX5Oc0i4msrY19eW1oUj+MqIyMZB6GqosWulNuIFxQpC0kFMhnkQfEj/AHH1VdGm+J7N0t7cLVVvh6ttYG1LjitktkfIeHrA+Ss5qlVpyinGppl5z0OpsruhWqQrWb3lGG645xJJdddH+S8yvuHGBxK02VZx7cRc4/8AcmrBt7sqPCTNsMSPpe2kkC9XB3dJcx17Ne3dkeDCNwzhRI51XOiJUeDr6xTZMhmLHYusdxx59aUIbSHUklSlcgB4nlSvVer9PQJjkm63R/Wl8xtKGn1JhNEZASt8+u6BjG1oJTg+q7XujSlNaFe92jSs2+JLGUtOeefTk/nojDiy4wNWynUSlPs+hxCH3U7SseitesQScZ+eqcp11Tfp+o7w9c55bQtzaEMspKWmkJSEpQkZPIJSkcySccyTzpsbIStKj0BBrZUKPCzrzOI2ptJXu4ksKK+vI2JYJd7LegL5DBz18KFRyl4NFxBWTjAz1+qtpUlD7iFdpla/fJUBkH6KFlKnksJ7QlK8AqUDjB+as5qjVGY7UrKlhtKBlSiOlb27eSopU5ghezkM92c17HIeEttBAU4QUgnHfS9DgccO3BCXcAjv9WhIybT2mwcznArZMYMd7syrdyyDjFKIyXUlbjUbevcdqyen0VksSlMKTIj9pjJCycFNCBMY57Nle4e6nA5dOeKzdidm06sryUL24x1pXHL/AKJG7FQAyd/MdM+dYzOcaTj44f6ChIndiIa5LkoCsZxtNAh57M9phKm+0UcdBSyWl5ShsQwUFIG9eOVanypp2IlCgcoCTjmCKA1pt5UN4dy2QClW3rmkr7fZvLbznacZp2A2uHcvbyAwdoCQPLNNcs/xtwnChuz5GhA8DThVAElFyiKJc2DBJQfmOOue7FDOnXFuQWlvqackoWpSVtYKNuOWM+dOcZ8m2x5JdajQnEqbRFDCnACCfWyDnORnNEiS9EkWVaXBKKwttC1hSSdxSMnOTUE4GRi2QZExiNGugeU6vacMKTtGCc8+vSkM+I7EmLjOIUFJVgZGCodxx51I2Vott5CEWMIQ2rCnUJW4en5OaSW5U1cyXMjWwy3Q6Q246T7kc9Np7+nzVIG++Wty1vttLXv7RsL3bcc+8fRW+FZ2ZFuVNVcmW0Ix2gKCdhJ5A09XONdAj0ZyGbo0tG/c5gKbWc5AI7vKktrYjp0+uA++hEieC40CeQCcbcnuyQaDAim2IRrc7L9K3lDLTm3s8Z3nGOvdTLU2vi1fg0+0QMJixj581/dUJoGFFFFCApw0688zeI/ZOrb3LAVtURkeBoorFX+Gy/sv8ZT9UbdUrWq8PIUtRQkjaknkOQ6U1UUVFv8ADR72v+NqeoUUUVmNaekk9TRk5zk5oooDytrLjicBK1JGc4B76KKAwKlZPrH668KlEYKifpoooDytgUrsCncdpV0zyoooDXW1S1EtZUfVAxz6UUUAo7Z741z7RpI4oqcUVEk56k0UUA626XKahoQ1JeQgZwlLhAHOtVxkyXH46nJDq1IVlJUskpOR08KKKEin2wn/AM+k/rVfvppded7ZxXarypRKjuPM560UUDPO2e+Nc+0a10UUIFypMlyE6hch1SSlCcFZIwDyH0UhoooD/9k=";
const LOGO_D = "data:image/png;base64,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";
const SYS_P = "당신은 SBTL 첨단소재 AI 어시스턴트.";

/* Data - loaded from /data/ at runtime */
const BRIEFING = {
  date:"2026.04.03", day:"목요일",
  cards:[
    {signal:"TOP",title:"미국 ESS 셀 제조, 국내 수요 100% 충족 — 한국 3사 80% 점유",fact:"2026년 미국 ESS 수요 60GWh 대비 FEOC 적합 생산 약 10% 과잉.",source:"ESC",impls:["EV→ESS 전환 시 파우치 vs 각형 비중 변화 모니터링"],color:"#E63946"},
    {signal:"HIGH",title:"K-배터리, 제품 경쟁 → 공급망 경쟁 전환",fact:"InterBattery 2026 이후 경쟁 축이 제조 거점·원재료 조달로 이동.",source:"SMM",impls:["소재 안정 공급 능력이 차별화 요소"],color:"#F4A261"},
    {signal:"HIGH",title:"Georgia Power 1GWh BESS 착공",fact:"260MW/1GWh, 2027 완공. Georgia PSC 총 9건 3GW+.",source:"ESS News",impls:[],color:"#F4A261"},
    {signal:"MID",title:"BESS 보험사, 변압기·시공 하자 리스크 주목",fact:"350MWh 시스템 BMS 미감지 불균형으로 용량 11% 좌초.",source:"ESS News",impls:[],color:"#457B9D"},
  ],
  policyChanges:[
    {id:"JP-004",change:"UPCOMING→ACTIVE",desc:"밸런싱 시장 가격상한 시행"},
    {id:"JP-005",change:"UPCOMING→ACTIVE",desc:"리튜이온 의무 리사이클링 발효"},
    {id:"JP-006",change:"UPCOMING→ACTIVE",desc:"BESS 접속 투기 방지 규제 시행"},
  ],
  comment:"미국 ESS 셀 시장에서 한국 3사가 FEOC 적합 용량의 80%를 차지한다는 건, EV 둔화가 오히려 ESS에서의 포지션을 강화하는 역설적 구조.",
};
const CD = {
  newsletter:[{id:1,title:"CEO 뉴스레터 Vol.06",subtitle:"K-배터리 미래 전략",date:"2026.03.28",isNew:true,color:"#E63946",likes:38},{id:2,title:"Vol.05",subtitle:"글로벌 공급망 변화",date:"2026.03.21",isNew:true,color:"#457B9D",likes:64},{id:3,title:"Vol.04",subtitle:"ESG 경영",date:"2026.03.14",isNew:false,color:"#2A9D8F",likes:89}],
  webtoon:[{id:1,title:"EP.07 전고체의 시대",subtitle:"K-Battery 2026",date:"2026.03.30",isNew:true,color:"#6C5CE7",likes:45},{id:2,title:"EP.06 리사이클링 혁명",subtitle:"K-Battery 2026",date:"2026.03.23",isNew:true,color:"#A29BFE",likes:78},{id:3,title:"EP.05 글로벌 배터리 전쟁",subtitle:"K-Battery 2026",date:"2026.03.16",isNew:false,color:"#FD79A8",likes:134}],
};
const TD = {meta:{total:49,lastUpdated:"2026.04.03"},summary:{ACTIVE:22,UPCOMING:12,WATCH:11,DONE:4},
  regions:[{code:"NA",flag:"🇺🇸",name:"북미",total:9,ACTIVE:3},{code:"EU",flag:"🇪🇺",name:"유럽",total:13,ACTIVE:4},{code:"CN",flag:"🇨🇳",name:"중국",total:9,ACTIVE:5},{code:"KR",flag:"🇰🇷",name:"한국",total:9,ACTIVE:4},{code:"JP",flag:"🇯🇵",name:"일본",total:9,ACTIVE:6}],
  upcoming:[{date:"Q2 초",title:"EU Battery Booster 공모",region:"EU"},{date:"05.04",title:"KR 배터리 정보공개 마감",region:"KR"},{date:"06.30",title:"NA §30C 세액공제 종료",region:"NA"}],
};
const CATS=[{key:"all",label:"홈",icon:"🏠"},{key:"newsletter",label:"뉴스레터",icon:"📨"},{key:"webtoon",label:"웹툰",icon:"🎨"},{key:"tracker",label:"트래커",icon:"📊"},{key:"chatbot",label:"AI 챗봇",icon:"🤖"}];
const CM={newsletter:{emoji:"📨",label:"뉴스레터"},webtoon:{emoji:"🎨",label:"웹툰"}};
const SC={ACTIVE:"#E63946",UPCOMING:"#F4A261",WATCH:"#457B9D",DONE:"#95A5A6"};
const SL={ACTIVE:"진행중",UPCOMING:"예정",WATCH:"모니터링",DONE:"완료"};
const sigC={TOP:"#E63946",HIGH:"#F4A261",MID:"#457B9D"};
const sigL={t:"🔴 TOP",h:"🟠 HIGH",m:"🔵 MID"};

const T=(dk)=>({
  bg:dk?"#0f1117":"#F8F9FC", card:dk?"#1a1f2e":"#FFFFFF", tx:dk?"#e8e8e8":"#1a1a2a",
  sub:dk?"#888":"#6b7280", brd:dk?"#252d3d":"#e5e7eb", sh:dk?"0 2px 8px rgba(0,0,0,0.3)":"0 2px 12px rgba(0,0,0,0.06)",
  hdr:dk?"linear-gradient(135deg,#1a1f2e,#0f1520)":"linear-gradient(135deg,#1e3a5f,#2d5a8e)",
});

/* Runtime data loading */
function useKnowledgeBase() {
  const [cards, setCards] = useState([]);
  const [faq, setFaq] = useState([]);
  const [loaded, setLoaded] = useState(false);
  useEffect(() => {
    Promise.all([
      fetch("/data/cards.json").then(r => r.json()).catch(() => ({cards:[]})),
      fetch("/data/faq.json").then(r => r.json()).catch(() => []),
    ]).then(([cardsData, faqData]) => {
      setCards(cardsData.cards || []);
      setFaq(faqData);
      setLoaded(true);
    });
  }, []);
  return { cards, faq, loaded };
}

function searchCards(CARDS, q) {
  const ws = q.toLowerCase().replace(/[?!.,]/g,"").split(/\s+/).filter(w=>w.length>=2);
  if(!ws.length) return [];
  return CARDS.map(c=>{let sc=0;const tl=c.T.toLowerCase(),gl=(c.g||"").toLowerCase(),ks=c.k||[];
    for(const w of ws){if(tl.includes(w))sc+=10;if(gl.includes(w))sc+=5;if(ks.some(k=>k.includes(w)||w.includes(k)))sc+=8;}
    if(c.s==="t")sc*=2;else if(c.s==="h")sc*=1.5;return{...c,sc};
  }).filter(c=>c.sc>0).sort((a,b)=>b.sc-a.sc).slice(0,3);
}
function fmtCards(cards){if(!cards.length)return null;let r="📚 SBTL 인사이트 DB:\n\n";
  cards.forEach((c,i)=>{r+=`${sigL[c.s]||""} ${c.T}\n`;if(c.f)r+=`${c.f}\n`;if(c.i?.length){r+="\n";c.i.forEach(imp=>{r+=`→ ${imp}\n`;});}if(i<cards.length-1)r+="\n---\n\n";});return r;}

function BriefingSection({dark}){
  const t=T(dark),b=BRIEFING;
  return(<div>
    <div style={{background:dark?"linear-gradient(135deg,#1a1025,#0f1520)":"linear-gradient(135deg,#f0f4ff,#e8edf8)",borderRadius:16,padding:"16px 16px 12px",marginBottom:10,border:dark?"none":"1px solid #e0e5f0"}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}>
        <div><h2 style={{fontSize:16,fontWeight:800,color:dark?"#fff":"#1a1a2a",margin:0}}>🔥 오늘의 브리핑</h2>
        <p style={{fontSize:11,color:t.sub,margin:"2px 0 0"}}>{b.date} {b.day} · {b.cards.length}건</p></div>
        <div style={{display:"flex",gap:4}}>{["TOP","HIGH","MID"].map(s=>{const n=b.cards.filter(c=>c.signal===s).length;return n?<span key={s} style={{fontSize:9,fontWeight:800,color:sigC[s],background:sigC[s]+"15",padding:"3px 7px",borderRadius:6}}>{s} {n}</span>:null;})}</div>
      </div>
    </div>
    {b.cards.map((c,i)=>(<div key={i} style={{background:t.card,borderRadius:14,padding:"13px 15px",marginBottom:8,borderLeft:`4px solid ${c.color}`,boxShadow:t.sh}}>
      <span style={{fontSize:9,fontWeight:800,color:sigC[c.signal],background:sigC[c.signal]+"12",padding:"2px 8px",borderRadius:5}}>{c.signal}</span>
      <h3 style={{fontSize:13,fontWeight:700,color:t.tx,margin:"6px 0 4px",lineHeight:1.4}}>{c.title}</h3>
      <p style={{fontSize:11,color:t.sub,lineHeight:1.5,margin:0}}>{c.fact}</p>
      {c.impls.length>0&&<div style={{marginTop:6,paddingTop:6,borderTop:`1px solid ${t.brd}`}}>{c.impls.map((imp,j)=>(<p key={j} style={{fontSize:11,color:t.sub,margin:"0 0 2px",paddingLeft:14,position:"relative",lineHeight:1.4}}><span style={{position:"absolute",left:0,color:"#E63946",fontWeight:700}}>→</span>{imp}</p>))}</div>}
    </div>))}
    {b.policyChanges.length>0&&<div style={{background:t.card,borderRadius:14,padding:"11px 13px",marginBottom:8,border:`1px solid ${t.brd}`,boxShadow:t.sh}}>
      <span style={{fontSize:11,fontWeight:700,color:"#6C5CE7"}}>🔔 정책 변경</span>
      {b.policyChanges.map((p,i)=>(<div key={i} style={{display:"flex",alignItems:"center",gap:6,marginTop:7}}>
        <div style={{width:5,height:5,borderRadius:3,background:"#E63946",flexShrink:0}}/>
        <span style={{fontSize:10,fontWeight:700,color:"#E63946",fontFamily:"monospace"}}>{p.id}</span>
        <span style={{fontSize:10,color:t.sub,background:dark?"#1a2030":"#f0f2f5",padding:"1px 6px",borderRadius:4}}>{p.change}</span>
        <span style={{fontSize:11,color:t.sub,flex:1}}>{p.desc}</span>
      </div>))}
    </div>}
    <div style={{background:dark?"linear-gradient(135deg,#1a1025,#0f1520)":"linear-gradient(135deg,#fff8f6,#fef5f0)",borderRadius:14,padding:"13px 15px",marginBottom:10,border:dark?"1px solid rgba(200,16,46,0.15)":"1px solid #fde8e0"}}>
      <span style={{fontSize:10,fontWeight:700,color:"#C8102E"}}>💬 CLAIRE'S NOTE</span>
      <p style={{fontSize:12,color:t.sub,lineHeight:1.55,margin:"5px 0 0",fontStyle:"italic"}}>{b.comment}</p>
    </div>
  </div>);
}

function Home({onNav,dark,cardCount}){
  const t=T(dark);
  return(<div style={{padding:"0 16px 120px",display:"flex",flexDirection:"column",gap:12}}>
    <BriefingSection dark={dark}/>
    <div>
      <div style={{display:"flex",justifyContent:"space-between",marginBottom:8}}><h3 style={{fontSize:14,fontWeight:700,color:t.tx,margin:0}}>📊 트래커</h3><button onClick={()=>onNav("tracker")} style={{fontSize:11,color:"#2d5a8e",fontWeight:600,border:"none",background:"none",cursor:"pointer"}}>전체 →</button></div>
      <div style={{display:"flex",gap:6}}>{TD.regions.map(r=>(<div key={r.code} style={{flex:1,background:t.card,borderRadius:12,padding:"10px 0",textAlign:"center",boxShadow:t.sh,border:`1px solid ${t.brd}`}}><div style={{fontSize:14}}>{r.flag}</div><div style={{fontSize:15,fontWeight:800,color:t.tx}}>{r.ACTIVE}</div><div style={{fontSize:8,color:t.sub,fontWeight:600}}>ACTIVE</div></div>))}</div>
    </div>
    <button onClick={()=>onNav("chatbot")} style={{background:dark?"linear-gradient(135deg,#1a1f2e,#0f3460)":"linear-gradient(135deg,#2d5a8e,#1e3a5f)",border:"none",borderRadius:14,padding:"16px 18px",cursor:"pointer",display:"flex",alignItems:"center",gap:12,boxShadow:"0 4px 16px rgba(30,58,95,0.2)"}}>
      <span style={{fontSize:22}}>🤖</span>
      <div style={{textAlign:"left"}}><h4 style={{color:"#fff",fontSize:14,fontWeight:700,margin:0}}>AI에게 물어보기</h4><p style={{color:"rgba(255,255,255,0.5)",fontSize:11,margin:0}}>FAQ + 카드 DB {cardCount}건 + Brave</p></div>
      <span style={{marginLeft:"auto",color:"rgba(255,255,255,0.4)"}}>→</span>
    </button>
  </div>);
}

function ChatBot({dark,CARDS,FAQ}){
  const t=T(dark);
  const cardCount = CARDS.length;
  const [msgs,setMsgs]=useState([{role:"assistant",content:`안녕하세요! SBTL AI 어시스턴트입니다. 🔋\n\n3단계 지식 엔진:\n💡 FAQ (${FAQ.length}건) → 📚 카드 DB (${cardCount}건) → 🔍 실시간 검색`,tier:null}]);
  const [input,setInput]=useState("");const [loading,setLoading]=useState(false);const [mode,setMode]=useState("");
  const endRef=useRef(null);useEffect(()=>{endRef.current?.scrollIntoView({behavior:"smooth"});},[msgs]);
  const tierL={faq:"💡 FAQ",cards:`📚 카드 DB (${cardCount}건)`,brave:"🔍 Brave Search",info:"💬 안내"};
  const matchFaq=(q)=>{const l=q.toLowerCase();for(const f of FAQ){if(f.k.some(k=>l.includes(k)))return f.a;}return null;};
  const searchBrave=async(q)=>{try{const r=await fetch("/api/brave",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:q+" battery ESS 2026"})});const d=await r.json();if(d.error)return null;const res=(d.web?.results||[]).slice(0,3);if(!res.length)return null;let rp="🔍 실시간 검색 결과:\n\n";res.forEach((r,i)=>{rp+=(i+1)+". "+r.title+"\n"+(r.description||"").substring(0,100)+"...\n\n";});return rp;}catch(e){return null;}};
  const send=async()=>{const txt=input.trim();if(!txt||loading)return;setInput("");const nm=[...msgs,{role:"user",content:txt}];setMsgs(nm);setLoading(true);
    setMode("FAQ");const fa=matchFaq(txt);if(fa){setMsgs(p=>[...p,{role:"assistant",content:fa,tier:"faq"}]);setLoading(false);return;}
    setMode(`카드 DB (${cardCount})`);const cr=searchCards(CARDS,txt);const ca=fmtCards(cr);if(ca){setMsgs(p=>[...p,{role:"assistant",content:ca,tier:"cards"}]);setLoading(false);return;}
    if(/(최신|뉴스|소식|현황|지금|오늘|어제|이번|최근|검색|찾아|가격|시세)/.test(txt)){setMode("Brave 검색");const br=await searchBrave(txt);if(br){setMsgs(p=>[...p,{role:"assistant",content:br,tier:"brave"}]);setLoading(false);return;}}
    setMsgs(p=>[...p,{role:"assistant",content:"이 질문에 대한 답변을 찾지 못했어요.\n\n다음을 시도해보세요:\n• 더 구체적인 키워드로 질문 (예: 'FEOC', 'LFP', '전고체')\n• 최신 뉴스는 '최신 배터리 뉴스'로 검색\n• 정책 관련은 트래커 탭에서 확인",tier:"info"}]);setLoading(false);
  };
  const qQ=["테슬라 LFP 계약?","FEOC가 뭐야?","알루미늄 가격?","ESS 골드러시?","전고체 배터리?"];
  return(<div style={{display:"flex",flexDirection:"column",height:"calc(100vh - 200px)"}}>
    <div style={{flex:1,overflowY:"auto",padding:"14px 14px 8px"}}>
      {msgs.length<=1&&<div style={{display:"flex",flexWrap:"wrap",gap:6,marginTop:8}}>{qQ.map(q=>(<button key={q} onClick={()=>setInput(q)} style={{background:t.card,border:`1px solid ${t.brd}`,borderRadius:20,padding:"8px 14px",fontSize:12,color:t.tx,cursor:"pointer",fontFamily:"inherit",boxShadow:t.sh}}>{q}</button>))}</div>}
      {msgs.map((m,i)=>(<div key={i} style={{display:"flex",justifyContent:m.role==="user"?"flex-end":"flex-start",marginBottom:12}}>
        {m.role==="assistant"&&<div style={{width:28,height:28,borderRadius:14,background:"linear-gradient(135deg,#2d5a8e,#1e3a5f)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:12,marginRight:8,flexShrink:0,marginTop:2}}>🤖</div>}
        <div style={{maxWidth:"80%"}}><div style={{padding:"11px 14px",fontSize:13,lineHeight:1.6,whiteSpace:"pre-wrap",wordBreak:"break-word",borderRadius:m.role==="user"?"16px 16px 4px 16px":"16px 16px 16px 4px",background:m.role==="user"?"#2d5a8e":t.card,color:m.role==="user"?"#fff":t.tx,boxShadow:t.sh}}>{m.content}</div>
        {m.tier&&<span style={{fontSize:9,color:t.sub,marginTop:3,display:"block",paddingLeft:4,opacity:0.7}}>{tierL[m.tier]}</span>}</div>
      </div>))}
      {loading&&<div style={{display:"flex",gap:8,marginBottom:12}}><div style={{width:28,height:28,borderRadius:14,background:"linear-gradient(135deg,#2d5a8e,#1e3a5f)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:12}}>🤖</div><div style={{background:t.card,padding:"11px 14px",borderRadius:"16px 16px 16px 4px",boxShadow:t.sh}}><div style={{display:"flex",alignItems:"center",gap:6}}><div style={{display:"flex",gap:3}}>{[0,1,2].map(i=>(<div key={i} style={{width:6,height:6,borderRadius:3,background:t.sub,animation:"pulse 1s ease "+(i*0.2)+"s infinite"}}/>))}</div><span style={{fontSize:10,color:t.sub}}>{mode}...</span></div></div></div>}
      <div ref={endRef}/>
    </div>
    <div style={{padding:"10px 14px 16px",background:dark?"#0a0d14":"#f0f2f5",borderTop:`1px solid ${t.brd}`}}><div style={{display:"flex",gap:8}}><input type="text" value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==="Enter"&&send()} placeholder="질문을 입력하세요..." style={{flex:1,padding:"11px 16px",borderRadius:24,border:`2px solid ${t.brd}`,fontSize:14,outline:"none",fontFamily:"inherit",background:dark?"#1a1f2e":"#fff",color:t.tx}} onFocus={e=>e.target.style.borderColor="#2d5a8e"} onBlur={e=>e.target.style.borderColor=t.brd}/><button onClick={send} disabled={loading||!input.trim()} style={{width:40,height:40,borderRadius:20,border:"none",background:input.trim()&&!loading?"#2d5a8e":"#ccc",color:"#fff",fontSize:16,cursor:input.trim()&&!loading?"pointer":"default",display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0}}>↑</button></div></div>
  </div>);
}

function Tracker({dark}){
  const t=T(dark),d=TD;
  return(<div style={{padding:"0 16px 120px",display:"flex",flexDirection:"column",gap:14}}>
    <div style={{background:dark?"linear-gradient(135deg,#1a1f2e,#0f3460)":"linear-gradient(135deg,#2d5a8e,#1e3a5f)",borderRadius:16,padding:"18px",color:"#fff",boxShadow:"0 4px 20px rgba(30,58,95,0.15)"}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:12}}><div><h2 style={{fontSize:17,fontWeight:800,margin:0}}>Policy Tracker</h2><p style={{fontSize:11,color:"rgba(255,255,255,0.5)",margin:"2px 0 0"}}>{d.meta.lastUpdated}</p></div><div style={{background:"rgba(255,255,255,0.15)",borderRadius:12,padding:"6px 14px"}}><span style={{fontSize:22,fontWeight:800}}>{d.meta.total}</span><span style={{fontSize:11,marginLeft:3,opacity:0.6}}>건</span></div></div>
      <div style={{display:"flex",gap:6}}>{Object.entries(d.summary).map(([s,n])=>(<div key={s} style={{flex:1,background:"rgba(255,255,255,0.1)",borderRadius:10,padding:"8px 0",textAlign:"center"}}><div style={{fontSize:18,fontWeight:800}}>{n}</div><div style={{fontSize:9,fontWeight:600,color:SC[s],marginTop:2}}>{SL[s]}</div></div>))}</div>
    </div>
    <div><h3 style={{fontSize:14,fontWeight:700,color:t.tx,margin:"0 0 8px"}}>권역별</h3><div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:8}}>{d.regions.map(r=>(<div key={r.code} style={{background:t.card,borderRadius:14,padding:"12px 14px",boxShadow:t.sh,border:`1px solid ${t.brd}`}}><span style={{fontSize:15,fontWeight:700}}>{r.flag} {r.name}</span><span style={{fontSize:12,float:"right",color:t.sub}}>{r.total}건</span><div style={{marginTop:6}}><span style={{fontSize:9,fontWeight:700,padding:"3px 8px",borderRadius:6,background:SC.ACTIVE+"12",color:SC.ACTIVE}}>ACTIVE {r.ACTIVE}</span></div></div>))}</div></div>
    <div><h3 style={{fontSize:14,fontWeight:700,color:t.tx,margin:"0 0 8px"}}>일정</h3><div style={{background:t.card,borderRadius:14,padding:"4px 0",boxShadow:t.sh,border:`1px solid ${t.brd}`}}>{d.upcoming.map((ev,i)=>(<div key={i} style={{padding:"10px 14px",display:"flex",alignItems:"center",gap:10,borderTop:i>0?`1px solid ${t.brd}`:"none"}}><span style={{width:40,fontSize:11,fontWeight:700,color:t.sub,fontFamily:"monospace",flexShrink:0}}>{ev.date}</span><div style={{width:6,height:6,borderRadius:3,background:"#E63946",flexShrink:0}}/><span style={{flex:1,fontSize:12,fontWeight:600,color:t.tx}}>{ev.title}</span><span style={{fontSize:10,color:t.sub,background:dark?"#1a2030":"#f0f2f5",padding:"2px 6px",borderRadius:4,flexShrink:0}}>{ev.region}</span></div>))}</div></div>
  </div>);
}

function Card({item,category,dark}){
  const t=T(dark);
  return(<div style={{background:t.card,borderRadius:16,overflow:"hidden",boxShadow:t.sh,border:`1px solid ${t.brd}`}}>
    <div style={{height:4,background:`linear-gradient(90deg,${item.color},${item.color}88)`}}/>
    <div style={{padding:"14px 16px"}}>
      <div style={{display:"flex",justifyContent:"space-between",marginBottom:5}}><span style={{fontSize:11,color:t.sub}}>{CM[category]?.emoji} {CM[category]?.label}</span>{item.isNew&&<span style={{fontSize:9,fontWeight:800,color:"#fff",background:"linear-gradient(135deg,#E63946,#ff6b6b)",padding:"2px 8px",borderRadius:8}}>NEW</span>}</div>
      <h3 style={{fontSize:15,fontWeight:700,color:t.tx,margin:"0 0 3px",lineHeight:1.35}}>{item.title}</h3>
      <p style={{fontSize:12,color:t.sub,margin:0}}>{item.subtitle}</p>
      <div style={{display:"flex",gap:12,fontSize:11,color:t.sub,marginTop:8}}>👍 {item.likes}<span style={{marginLeft:8}}>{item.date}</span></div>
    </div>
  </div>);
}

export default function App(){
  const [tab,setTab]=useState("all");const [dark,setDark]=useState(false);
  const {cards:CARDS, faq:FAQ, loaded} = useKnowledgeBase();
  const t=T(dark);
  const nc=Object.keys(CD).reduce((a,c)=>a+CD[c].filter(i=>i.isNew).length,0);
  const isCT=["newsletter","webtoon"].includes(tab);
  const fi=isCT?CD[tab]?.map(i=>({...i,category:tab}))||[]:[];

  if(!loaded) return(<div style={{maxWidth:480,margin:"0 auto",background:t.bg,minHeight:"100vh",display:"flex",alignItems:"center",justifyContent:"center",fontFamily:"'Pretendard',sans-serif"}}>
    <div style={{textAlign:"center"}}><div style={{fontSize:40,marginBottom:12}}>🔋</div><p style={{color:t.sub,fontSize:14}}>데이터 로딩 중...</p></div>
  </div>);

  return(<div style={{maxWidth:480,margin:"0 auto",background:t.bg,minHeight:"100vh",fontFamily:"'Pretendard',-apple-system,sans-serif",position:"relative",transition:"all 0.3s"}}>
    <style dangerouslySetInnerHTML={{__html:"@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}*{margin:0;padding:0;box-sizing:border-box}body{margin:0}"}}/>
    <div style={{background:t.hdr,padding:"20px 20px 24px",position:"relative"}}>
      <div style={{display:"flex",alignItems:"center",justifyContent:"space-between"}}>
        <div style={{display:"flex",alignItems:"center",gap:10}}>
          <img src={dark?LOGO_D:LOGO_D} alt="SBTL" style={{height:30,objectFit:"contain"}}/>
          {nc>0&&<div style={{background:"rgba(230,57,70,0.2)",borderRadius:10,padding:"3px 9px",display:"flex",alignItems:"center",gap:4}}><div style={{width:5,height:5,borderRadius:3,background:"#E63946",animation:"pulse 2s ease infinite"}}/><span style={{fontSize:10,color:"#E63946",fontWeight:700}}>{nc} new</span></div>}
        </div>
        <button onClick={()=>setDark(!dark)} style={{background:"rgba(255,255,255,0.15)",border:"none",borderRadius:12,width:36,height:36,display:"flex",alignItems:"center",justifyContent:"center",cursor:"pointer",fontSize:16}}>{dark?"☀️":"🌙"}</button>
      </div>
      <div style={{marginTop:14}}>
        <h1 style={{color:"#fff",fontSize:21,fontWeight:800,margin:0,letterSpacing:-0.5}}>{{tracker:"Policy Tracker",chatbot:"AI 챗봇"}[tab]||"콘텐츠 허브"}</h1>
        <p style={{color:"rgba(255,255,255,0.55)",fontSize:12,margin:"3px 0 0"}}>{{tracker:"5개 권역 정책 현황",chatbot:`FAQ ${FAQ.length} + Cards ${CARDS.length} + Brave`}[tab]||"Battery · ESS · EV Supply Chain Intelligence"}</p>
      </div>
      <div style={{position:"absolute",bottom:0,left:0,right:0,height:3,background:tab==="chatbot"?"linear-gradient(90deg,#6C5CE7,#A29BFE,#6C5CE7)":"linear-gradient(90deg,#2d5a8e,#4a90d9,#2d5a8e)"}}/>
    </div>
    {tab==="all"?<div style={{paddingTop:14}}><Home onNav={setTab} dark={dark} cardCount={CARDS.length}/></div>
     :tab==="chatbot"?<ChatBot dark={dark} CARDS={CARDS} FAQ={FAQ}/>
     :tab==="tracker"?<div style={{paddingTop:14}}><Tracker dark={dark}/></div>
     :isCT?<div style={{padding:"14px 16px 120px",display:"flex",flexDirection:"column",gap:12}}>{fi.map((item,i)=>(<Card key={i} item={item} category={item.category} dark={dark}/>))}</div>
     :null}
    <div style={{position:"fixed",bottom:0,left:"50%",transform:"translateX(-50%)",width:"100%",maxWidth:480,background:dark?"#111":"#fff",borderTop:`1px solid ${t.brd}`,display:"flex",padding:"8px 6px 16px",zIndex:100,boxShadow:"0 -4px 20px rgba(0,0,0,0.06)"}}>
      {CATS.map(cat=>{const isA=tab===cat.key;const cn=cat.key==="all"?BRIEFING.cards.length:cat.key==="tracker"?BRIEFING.policyChanges.length:cat.key==="chatbot"?0:(CD[cat.key]?.filter(i=>i.isNew).length||0);
        return(<button key={cat.key} onClick={()=>setTab(cat.key)} style={{display:"flex",flexDirection:"column",alignItems:"center",gap:3,padding:"6px 0",cursor:"pointer",border:"none",background:"none",flex:1,minWidth:0,position:"relative"}}>
          <div style={{position:"relative"}}><span style={{fontSize:20,lineHeight:1,filter:isA?"none":"grayscale(0.5) opacity(0.6)"}}>{cat.icon}</span>{cn>0&&<div style={{position:"absolute",top:-5,right:-9,background:"linear-gradient(135deg,#E63946,#ff6b6b)",color:"#fff",fontSize:8,fontWeight:800,minWidth:15,height:15,borderRadius:8,display:"flex",alignItems:"center",justifyContent:"center",padding:"0 3px",border:`2px solid ${dark?"#111":"#fff"}`}}>{cn}</div>}</div>
          <span style={{fontSize:10,fontWeight:isA?700:500,color:isA?"#2d5a8e":t.sub}}>{cat.label}</span>
          {isA&&<div style={{position:"absolute",top:0,left:"50%",transform:"translateX(-50%)",width:20,height:2.5,borderRadius:2,background:"#2d5a8e"}}/>}
        </button>);
      })}
    </div>
  </div>);
}
