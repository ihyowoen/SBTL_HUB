var fs = require('fs');
var path = require('path');

var dataPath = path.join(__dirname, 'tracker_data.json');
// Local: outputs to ./output/  |  Claude: outputs to /mnt/user-data/outputs/
var outputDir = fs.existsSync('/mnt/user-data/outputs') ? '/mnt/user-data/outputs' : path.join(__dirname, 'output');
if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, {recursive: true});
var outputPath = path.join(outputDir, 'battery_policy_tracker_2026_internal.html');

var raw = fs.readFileSync(dataPath, 'utf-8');
var data = JSON.parse(raw);
var meta = data.meta;
var sources = data.sources;
var items = data.items;
meta.totalItems = items.length;

// ─ Source Directory (Tier 1 + Tier 2) ─
function renderSourceDir() {
  var regions = ['NA','EU','CN','KR','JP'];
  var flags = {NA:'\u{1F1FA}\u{1F1F8}',EU:'\u{1F1EA}\u{1F1FA}',CN:'\u{1F1E8}\u{1F1F3}',KR:'\u{1F1F0}\u{1F1F7}',JP:'\u{1F1EF}\u{1F1F5}'};
  return regions.map(function(r) {
    var s = sources[r] || {};
    var t1 = (s.tier1||s||[]);
    var t2 = (s.tier2||[]);
    // Handle both old flat array and new tier structure
    if (Array.isArray(s)) { t1 = s; t2 = []; }

    var t1html = t1.map(function(x) {
      return '<li><a href="' + (x.url||x.u||'') + '" target="_blank">' + (x.name||x.n||'') + '</a></li>';
    }).join('');
    var t2html = t2.length > 0 ? '<li class="tier-sep">TIER 2 \u2014 \uBD84\uC11D\u00B7\uBCF4\uB3C4</li>' + t2.map(function(x) {
      return '<li class="t2"><a href="' + (x.url||x.u||'') + '" target="_blank">' + (x.name||x.n||'') + '</a></li>';
    }).join('') : '';

    return '<div class="dir-card"><h3>' + flags[r] + ' ' + r + '</h3>'
      + '<div class="tier-label">TIER 1 \u2014 1\uCC28 \uCD9C\uCC98</div>'
      + '<ul>' + t1html + t2html + '</ul></div>';
  }).join('');
}

// ─ Client-side JS ─
var clientJS = 'var DATA=' + JSON.stringify(items) + ';'
+'var SO={ACTIVE:0,DONE:1,UPCOMING:2,WATCH:3};'
+'var regionFilter="ALL",statusFilter="ALL";'
+'function render(){'
+'var grid=document.getElementById("itemsGrid");'
+'var f=DATA.slice();'
+'if(regionFilter!=="ALL")f=f.filter(function(i){return i.r===regionFilter});'
+'if(statusFilter!=="ALL")f=f.filter(function(i){return i.s===statusFilter});'
+'f.sort(function(a,b){return(SO[a.s]||9)-(SO[b.s]||9)});'
+'var FL={NA:"\u{1F1FA}\u{1F1F8}",EU:"\u{1F1EA}\u{1F1FA}",CN:"\u{1F1E8}\u{1F1F3}",KR:"\u{1F1F0}\u{1F1F7}",JP:"\u{1F1EF}\u{1F1F5}"};'
+'var SC={DONE:"st-done",ACTIVE:"st-active",UPCOMING:"st-upcoming",WATCH:"st-watch"};'
+'var SL={DONE:"\u2705 DONE",ACTIVE:"\u{1F534} ACTIVE",UPCOMING:"\u23ED UPCOMING",WATCH:"\u{1F441} WATCH"};'
+'grid.innerHTML=f.map(function(i){'
+'var sh=(i.src||[]).map(function(s){return\'<a href="\'+s.u+\'" target="_blank">\'+s.n+\'</a>\';}).join("");'
+'return\'<div class="item-card" data-region="\'+i.r+\'">\''
+'+\'<div class="item-region"><span class="flag">\'+FL[i.r]+\'</span>\'+i.r+\'</div>\''
+'+\'<div class="item-status \'+SC[i.s]+\'">\'+SL[i.s]+\'</div>\''
+'+\'<div class="item-body">\''
+'+\'<div class="item-title">\'+i.t+\'</div>\''
+'+\'<div class="item-desc">\'+i.d+\'</div>\''
+'+\'<div class="item-date">\'+i.dt+\'</div>\''
+'+(i.lastChecked?\'<div class="item-checked">\u{1F50D} last checked: \'+i.lastChecked+(i.checkNote?\' — \'+i.checkNote:\'\')+\'</div>\':\'\')'
+'+\'<div class="item-id">\'+i.id+\'</div>\''
+'+(i.tip?\'<div class="item-tip">\u{1F4A1} \'+i.tip+\'</div>\':\'\')'
+'+(i.detail?\'<div class="detail-toggle" onclick="toggleDetail(this)">\u25BC \uC790\uC138\uD788</div><div class="item-detail">\'+i.detail.replace(/\\n/g,\"<br>\")+\'</div>\':\'\')+\'</div>\''
+'+\'<div class="item-sources"><div class="src-label">SOURCES</div>\'+sh+\'</div></div>\';'
+'}).join("");'
+'document.getElementById("countBadge").textContent=f.length+" / "+DATA.length+" items";'
+'}'
+'document.getElementById("regionTabs").addEventListener("click",function(e){'
+'if(!e.target.classList.contains("tab-btn"))return;'
+'regionFilter=e.target.dataset.region;'
+'document.querySelectorAll("#regionTabs .tab-btn").forEach(function(b){b.classList.remove("active")});'
+'e.target.classList.add("active");render();'
+'});'
+'document.getElementById("statusFilters").addEventListener("click",function(e){'
+'if(!e.target.classList.contains("filter-pill"))return;'
+'statusFilter=e.target.dataset.status;'
+'document.querySelectorAll("#statusFilters .filter-pill").forEach(function(b){b.classList.remove("active")});'
+'e.target.classList.add("active");render();'
+'});'
+'render();'
+'function toggleDetail(el){'
+'var d=el.nextElementSibling;'
+'if(d.style.display==="block"){'
+'d.style.display="none";el.textContent="\u25BC \uC790\uC138\uD788";'
+'}else{'
+'d.style.display="block";el.textContent="\u25B2 \uC811\uAE30";'
+'}'
+'}';

// ─ CSS ─
var CSS = ':root{--bg:#0b0f1a;--bg2:#111827;--bg3:#1a2234;--bg4:#243049;--border:#1e293b;--border2:#2d3a50;--blue:#3b82f6;--cyan:#06b6d4;--green:#10b981;--amber:#f59e0b;--red:#ef4444;--rose:#f43f5e;--purple:#8b5cf6;--t1:#f1f5f9;--t2:#94a3b8;--t3:#64748b;--done-bg:rgba(16,185,129,.12);--done-c:#6ee7b7;--active-bg:rgba(239,68,68,.12);--active-c:#fca5a5;--upcoming-bg:rgba(59,130,246,.12);--upcoming-c:#93bbfd;--watch-bg:rgba(245,158,11,.12);--watch-c:#fcd34d}'
+'*{margin:0;padding:0;box-sizing:border-box}'
+'body{background:var(--bg);color:var(--t1);font-family:"Noto Sans KR",sans-serif;min-height:100vh}'
+'a{color:var(--cyan);text-decoration:none}a:hover{text-decoration:underline;opacity:.9}'
+'.shell{max-width:1200px;margin:0 auto;padding:24px 28px 40px}'
+'.top-bar{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:24px;flex-wrap:wrap;gap:12px}'
+'.top-bar h1{font-size:22px;font-weight:900;letter-spacing:-.3px}'
+'.top-bar h1 span{color:var(--cyan);font-weight:400;font-size:13px;margin-left:8px;letter-spacing:1px}'
+'.meta-line{font-family:"JetBrains Mono",monospace;font-size:10px;color:var(--t3);letter-spacing:1px}'
+'.tab-row{display:flex;gap:6px;margin-bottom:16px;flex-wrap:wrap}'
+'.tab-btn{font-family:"JetBrains Mono",monospace;font-size:11px;letter-spacing:1px;padding:6px 14px;border-radius:6px;border:1px solid var(--border);background:var(--bg2);color:var(--t3);cursor:pointer;transition:.15s}'
+'.tab-btn:hover{border-color:var(--border2);color:var(--t2)}'
+'.tab-btn.active{background:var(--bg3);color:var(--t1);border-color:var(--cyan)}'
+'.tab-btn[data-region="NA"].active{border-color:var(--blue);color:var(--blue)}'
+'.tab-btn[data-region="EU"].active{border-color:var(--cyan);color:var(--cyan)}'
+'.tab-btn[data-region="CN"].active{border-color:var(--red);color:var(--red)}'
+'.tab-btn[data-region="KR"].active{border-color:var(--green);color:var(--green)}'
+'.tab-btn[data-region="JP"].active{border-color:var(--rose);color:var(--rose)}'
+'.filter-bar{display:flex;gap:8px;margin-bottom:20px;align-items:center;flex-wrap:wrap}'
+'.filter-bar label{font-family:"JetBrains Mono",monospace;font-size:9px;color:var(--t3);letter-spacing:1.5px;text-transform:uppercase}'
+'.filter-pill{font-size:10px;padding:4px 10px;border-radius:4px;border:1px solid var(--border);background:var(--bg2);color:var(--t3);cursor:pointer;font-family:"JetBrains Mono",monospace;transition:.15s}'
+'.filter-pill:hover{color:var(--t2)}'
+'.filter-pill.active{color:var(--t1);border-color:var(--t3)}'
+'.filter-pill.s-done.active{color:var(--done-c);border-color:var(--done-c);background:var(--done-bg)}'
+'.filter-pill.s-active.active{color:var(--active-c);border-color:var(--active-c);background:var(--active-bg)}'
+'.filter-pill.s-upcoming.active{color:var(--upcoming-c);border-color:var(--upcoming-c);background:var(--upcoming-bg)}'
+'.filter-pill.s-watch.active{color:var(--watch-c);border-color:var(--watch-c);background:var(--watch-bg)}'
+'.count-badge{font-family:"JetBrains Mono",monospace;font-size:10px;color:var(--t3);margin-left:auto}'
+'.items-grid{display:flex;flex-direction:column;gap:8px}'
+'.item-card{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:14px 16px;display:grid;grid-template-columns:90px 60px 1fr 200px;gap:12px;align-items:start;transition:.15s;position:relative;overflow:hidden}'
+'.item-card::before{content:"";position:absolute;top:0;left:0;width:3px;height:100%}'
+'.item-card[data-region="NA"]::before{background:var(--blue)}'
+'.item-card[data-region="EU"]::before{background:var(--cyan)}'
+'.item-card[data-region="CN"]::before{background:var(--red)}'
+'.item-card[data-region="KR"]::before{background:var(--green)}'
+'.item-card[data-region="JP"]::before{background:var(--rose)}'
+'.item-card:hover{border-color:var(--border2)}'
+'.item-region{font-family:"JetBrains Mono",monospace;font-size:10px;letter-spacing:1.5px;display:flex;align-items:center;gap:5px}'
+'.item-region .flag{font-size:14px}'
+'.item-status{font-family:"JetBrains Mono",monospace;font-size:9px;padding:3px 7px;border-radius:3px;text-align:center;white-space:nowrap;align-self:start;margin-top:1px}'
+'.st-done{background:var(--done-bg);color:var(--done-c)}'
+'.st-active{background:var(--active-bg);color:var(--active-c)}'
+'.st-upcoming{background:var(--upcoming-bg);color:var(--upcoming-c)}'
+'.st-watch{background:var(--watch-bg);color:var(--watch-c)}'
+'.item-body{min-width:0}'
+'.item-title{font-size:13px;font-weight:600;color:var(--t1);margin-bottom:3px;line-height:1.4}'
+'.item-desc{font-size:11px;color:var(--t2);line-height:1.5;margin-bottom:4px}'
+'.item-date{font-family:"JetBrains Mono",monospace;font-size:9px;color:var(--t3)}'
+'.item-checked{font-family:"JetBrains Mono",monospace;font-size:8px;color:var(--t3);opacity:.5;margin-top:2px;line-height:1.4}'
+'.item-id{font-family:"JetBrains Mono",monospace;font-size:8px;color:var(--t3);opacity:.5;margin-top:2px}'
+'.item-tip{font-size:10px;color:var(--amber);background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.15);border-radius:4px;padding:5px 8px;margin-top:6px;line-height:1.45;font-family:"Noto Sans KR",sans-serif}'
+'.detail-toggle{font-family:"JetBrains Mono",monospace;font-size:9px;color:var(--cyan);cursor:pointer;margin-top:6px;padding:2px 0;opacity:.7;transition:.15s}'
+'.detail-toggle:hover{opacity:1}'
+'.item-detail{display:none;font-size:10px;color:var(--t2);background:rgba(6,182,212,.04);border:1px solid rgba(6,182,212,.1);border-radius:4px;padding:8px 10px;margin-top:4px;line-height:1.6;font-family:"Noto Sans KR",sans-serif;white-space:pre-line}'
+'.item-sources{display:flex;flex-direction:column;gap:3px}'
+'.item-sources a{font-family:"JetBrains Mono",monospace;font-size:9px;padding:2px 6px;background:rgba(6,182,212,.06);border:1px solid rgba(6,182,212,.12);border-radius:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:200px;display:block}'
+'.src-label{font-family:"JetBrains Mono",monospace;font-size:8px;color:var(--t3);letter-spacing:1px;margin-bottom:2px}'
+'.directory{margin-top:32px}'
+'.dir-title{font-family:"JetBrains Mono",monospace;font-size:11px;letter-spacing:2px;color:var(--t3);margin-bottom:12px;display:flex;align-items:center;gap:10px}'
+'.dir-title::after{content:"";flex:1;height:1px;background:var(--border)}'
+'.dir-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:10px}'
+'.dir-card{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:12px 14px;position:relative;overflow:hidden}'
+'.dir-card::before{content:"";position:absolute;top:0;left:0;width:100%;height:2px}'
+'.dir-card:nth-child(1)::before{background:var(--blue)}'
+'.dir-card:nth-child(2)::before{background:var(--cyan)}'
+'.dir-card:nth-child(3)::before{background:var(--red)}'
+'.dir-card:nth-child(4)::before{background:var(--green)}'
+'.dir-card:nth-child(5)::before{background:var(--rose)}'
+'.dir-card h3{font-size:12px;font-weight:700;margin-bottom:8px}'
+'.dir-card ul{list-style:none;display:flex;flex-direction:column;gap:4px}'
+'.dir-card li a{font-size:10px;color:var(--t2);display:block;padding:2px 0}'
+'.dir-card li a:hover{color:var(--cyan)}'
+'.dir-card .tier-label{font-family:"JetBrains Mono",monospace;font-size:7px;letter-spacing:1.5px;color:var(--cyan);margin-bottom:6px;opacity:.7}'
+'.dir-card .tier-sep{font-family:"JetBrains Mono",monospace;font-size:7px;letter-spacing:1.5px;color:var(--t3);margin-top:8px;padding-top:6px;border-top:1px dashed rgba(255,255,255,.06);opacity:.6}'
+'.dir-card li.t2 a{opacity:.6}'
+'.tracker-footer{margin-top:28px;padding-top:14px;border-top:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}'
+'.tracker-footer span{font-family:"JetBrains Mono",monospace;font-size:9px;color:var(--t3);letter-spacing:.5px}'
+'@media(max-width:900px){.item-card{grid-template-columns:70px 50px 1fr;gap:8px}.item-sources{display:none}.dir-grid{grid-template-columns:repeat(2,1fr)}}';

var updatedStr = meta.lastUpdated.replace('T',' ').substring(0,16);

var html = '<!DOCTYPE html>\n<html lang="ko">\n<head>\n<meta charset="UTF-8">\n'
+'<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
+'<title>Battery Policy Tracker 2026 \u2014 Internal</title>\n'
+'<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">\n'
+'<style>' + CSS + '</style>\n</head>\n<body>\n<div class="shell">\n'
+'<div class="top-bar"><div>\n'
+'<h1>Battery Policy Tracker 2026 <span>INTERNAL</span></h1>\n'
+'<div class="meta-line">5-REGION \u00B7 FULL-YEAR \u00B7 LAST UPDATED: ' + updatedStr + ' KST \u00B7 ' + items.length + ' ITEMS</div>\n'
+'</div></div>\n'
+'<div class="tab-row" id="regionTabs">\n'
+'<button class="tab-btn active" data-region="ALL">ALL</button>\n'
+'<button class="tab-btn" data-region="NA">\u{1F1FA}\u{1F1F8} NA</button>\n'
+'<button class="tab-btn" data-region="EU">\u{1F1EA}\u{1F1FA} EU</button>\n'
+'<button class="tab-btn" data-region="CN">\u{1F1E8}\u{1F1F3} CN</button>\n'
+'<button class="tab-btn" data-region="KR">\u{1F1F0}\u{1F1F7} KR</button>\n'
+'<button class="tab-btn" data-region="JP">\u{1F1EF}\u{1F1F5} JP</button>\n'
+'</div>\n'
+'<div class="filter-bar" id="statusFilters">\n'
+'<label>STATUS</label>\n'
+'<button class="filter-pill active" data-status="ALL">All</button>\n'
+'<button class="filter-pill s-done" data-status="DONE">\u2705 Done</button>\n'
+'<button class="filter-pill s-active" data-status="ACTIVE">\u{1F534} Active</button>\n'
+'<button class="filter-pill s-upcoming" data-status="UPCOMING">\u23ED Upcoming</button>\n'
+'<button class="filter-pill s-watch" data-status="WATCH">\u{1F441} Watch</button>\n'
+'<span class="count-badge" id="countBadge"></span>\n'
+'</div>\n'
+'<div class="items-grid" id="itemsGrid"></div>\n'
+'<div class="directory">\n'
+'<div class="dir-title">MONITORING SOURCE DIRECTORY</div>\n'
+'<div class="dir-grid">' + renderSourceDir() + '</div>\n'
+'</div>\n'
+'<div class="tracker-footer">\n'
+'<span>Battery Intelligence \u2014 Internal Policy Tracker v' + meta.version + '</span>\n'
+'<span>LAST VERIFIED: ' + meta.lastUpdated.substring(0,10) + '</span>\n'
+'</div>\n</div>\n'
+'<script>\n' + clientJS + '\n</script>\n'
+'</body>\n</html>';

fs.writeFileSync(outputPath, html, 'utf-8');
console.log('Output: ' + outputPath);
console.log('Items: ' + items.length + ' | Updated: ' + meta.lastUpdated);
