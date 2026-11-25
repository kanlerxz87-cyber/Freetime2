
function byId(id){return document.getElementById(id)}
function fmtDate(d){return new Date(d+'T00:00:00').toLocaleDateString(undefined,{weekday:'short',year:'numeric',month:'short',day:'numeric'})}
function badge(v){const m={verified:'b-verified',estimated:'b-estimated',tbd:'b-tbd',unverified:'b-unverified'};const cls=m[v]||'b-unverified';return `<span class="badge ${cls}">${(v||'unverified').toUpperCase()}</span>`}
function prio(p){return p==='high'?'<span class="badge b-high">HIGH</span>':'<span class="badge b-normal">NORMAL</span>'}
function srcLinks(ids){return (ids||[]).map(id=>{const s=SOURCES.find(x=>x.id===id);return s?`<a href="${s.url}" target="_blank" rel="noopener">${id}</a>`:id}).join(', ')||'<span class="badge b-unverified">NO SOURCE</span>'}
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}

function renderSourcesTable(targetId){
  const el=byId(targetId); if(!el) return;
  el.innerHTML=`<div class="table-wrap"><table><thead><tr><th>ID</th><th>Source</th><th>Type</th><th>Accessed</th><th>Notes</th></tr></thead><tbody>`+
  SOURCES.map(s=>`<tr><td>${esc(s.id)}</td><td><a href="${s.url}" target="_blank" rel="noopener">${esc(s.name)}</a><div class="small">${esc(s.url)}</div></td><td>${esc(s.type)}</td><td>${esc(s.accessed)}</td><td>${esc(s.notes||'')}</td></tr>`).join('')+
  `</tbody></table></div>`;
}

function overlaps(aStart,aEnd,bStart,bEnd){return aStart<=bEnd && bStart<=aEnd}
function iso(d){return d.toISOString().slice(0,10)}
function addDays(isoStr,n){const d=new Date(isoStr+'T00:00:00Z'); d.setUTCDate(d.getUTCDate()+n); return iso(d)}

function windowsCoveringDate(dateStr){
  return SEASON_WINDOWS.filter(w=>dateStr>=w.start && dateStr<=w.end);
}
function eventsOnDate(dateStr){
  return (typeof EVENTS!=='undefined'?EVENTS:[]).filter(e=>e.date===dateStr);
}

function isFreeDate(dateStr){
  // Free means none of the blocking high-priority scope events/windows are on air.
  // We treat any window in SEASON_WINDOWS that includes MLB/NFL/NCAAF Stanford/Cal/Westwood One as blocking.
  const ws = windowsCoveringDate(dateStr);
  const blocking = ws.filter(w=>/MLB|NFL|NCAAF/.test(w.sport));
  // Also check specific events
  const ev = eventsOnDate(dateStr).filter(e=>['MLB','NFL','NCAAF'].includes(e.sport));
  return {free: blocking.length===0 && ev.length===0, blocking, ev};
}

function findFreeRuns(start,end,minDays){
  const runs=[]; let cur=null;
  let d=start;
  while(d<=end){
    const st=isFreeDate(d);
    if(st.free){ if(!cur) cur={start:d,end:d,days:1}; else {cur.end=d; cur.days++;} }
    else { if(cur && cur.days>=minDays) runs.push(cur); cur=null; }
    d=addDays(d,1);
  }
  if(cur && cur.days>=minDays) runs.push(cur);
  return runs;
}

function sourcesForYear(year){
  const from=`${year}-01-01`, to=`${year}-12-31`;
  return [...new Set(SEASON_WINDOWS.filter(w=>w.start<=to && w.end>=from).flatMap(w=>w.sourceIds||[]))];
}

function renderVacation(targetId, year){
  const el=byId(targetId); if(!el) return;
  const start=`${year}-01-01`, end=`${year}-12-31`;
  const runs7=findFreeRuns(start,end,7);
  const runs14=findFreeRuns(start,end,14);
  const runs21=findFreeRuns(start,end,21);
  const shortRuns=findFreeRuns(start,end,3).filter(r=>r.days<7).sort((a,b)=>b.days-a.days).slice(0,8);
  const modelSources=srcLinks(sourcesForYear(year));
  function list(runs,label){
    if(!runs.length) return `<div class="warn"><strong>No ${label}+ consecutive fully-free days found</strong> in ${year} under the strict "no MLB preseason/regular/postseason, no NFL preseason/regular/postseason, no Stanford/Cal NCAAF" window model. See partial/shoulder windows below and flagged caveats.</div>`;
    return `<div class="table-wrap"><table><thead><tr><th>Start</th><th>End</th><th>Days</th><th>Status</th><th>Model sources</th><th>Notes</th></tr></thead><tbody>`+
      runs.map(r=>`<tr><td>${fmtDate(r.start)}</td><td>${fmtDate(r.end)}</td><td><strong>${r.days}</strong></td><td>${badge('estimated')}</td><td>${modelSources}</td><td>Based on season-window model; individual game times not released for most ${year} games. Verify before booking.</td></tr>`).join('')+
      `</tbody></table></div>`;
  }
  el.innerHTML = `
    <div class="card"><h3>${year} &mdash; 7+ day windows (strict model)</h3>${list(runs7,7)}</div>
    <div class="card" style="margin-top:12px"><h3>${year} &mdash; 14+ day windows (strict model)</h3>${list(runs14,14)}</div>
    <div class="card" style="margin-top:12px"><h3>${year} &mdash; 21+ day windows (strict model)</h3>${list(runs21,21)}</div>
    <div class="card" style="margin-top:12px"><h3>${year} &mdash; Shorter 3–6 day model gaps</h3>${shortRuns.length?`<div class="warn">No 7+ day run in the current model. The longest shorter candidates are below; all dates are estimates and are not booking-grade verified.</div><div class="table-wrap"><table><thead><tr><th>Start</th><th>End</th><th>Days</th><th>Status</th><th>Model sources</th><th>Limitation</th></tr></thead><tbody>${shortRuns.map(r=>`<tr><td>${fmtDate(r.start)}</td><td>${fmtDate(r.end)}</td><td>${r.days}</td><td>${badge('estimated')}</td><td>${modelSources}</td><td>Model-based gap between broad league windows; full daily schedules/radio carriage missing.</td></tr>`).join('')}</tbody></table></div>`:`<div class="small">No 3–6 day model gaps detected.</div>`}</div>
  `;
}

function renderWindowsTable(targetId){
  const el=byId(targetId); if(!el) return;
  const rows=[...SEASON_WINDOWS].sort((a,b)=>a.start.localeCompare(b.start));
  el.innerHTML=`<div class="table-wrap"><table><thead><tr><th>Start</th><th>End</th><th>Sport</th><th>Scope</th><th>Priority</th><th>Status</th><th>Sources</th><th>Notes</th></tr></thead><tbody>`+
  rows.map(w=>`<tr><td>${esc(w.start)}</td><td>${esc(w.end)}</td><td>${esc(w.sport)}</td><td>${esc(w.scope)}</td><td>${prio(w.priority)}</td><td>${badge(w.verification)}</td><td>${srcLinks(w.sourceIds)}</td><td>${esc(w.notes||'')}</td></tr>`).join('')+
  `</tbody></table></div>`;
}

function renderEventsTable(targetId){
  const el=byId(targetId); if(!el) return;
  const rows=[...EVENTS].sort((a,b)=>(a.date+a.time).localeCompare(b.date+b.time));
  el.innerHTML=`<div class="table-wrap"><table><thead><tr><th>Date</th><th>Time (PT)</th><th>Sport</th><th>Teams / Event</th><th>Priority</th><th>Radio (SF AM/FM)</th><th>Status</th><th>Sources</th><th>Notes</th></tr></thead><tbody>`+
  rows.map(e=>`<tr><td>${esc(e.date)}</td><td>${esc(e.time)} ${esc(e.tz||'')}</td><td>${esc(e.sport)}</td><td>${esc(e.teams)}</td><td>${prio(e.priority)}</td><td>${esc(e.radio||'')}</td><td>${badge(e.verification)}</td><td>${srcLinks(e.sourceIds)}</td><td>${esc(e.notes||'')}</td></tr>`).join('')+
  `</tbody></table></div>`;
}

function clockText(min){
  const norm=((min%1440)+1440)%1440;
  return `${String(Math.floor(norm/60)).padStart(2,'0')}:${String(norm%60).padStart(2,'0')}`;
}
function renderCalendar(targetId, controlsId){
  const el=byId(targetId), ctl=byId(controlsId); if(!el||!ctl) return;
  const today='2026-11-25';
  ctl.innerHTML=`<div class="controls">
    <button class="btn" id="cal-prev">◀ Yesterday</button>
    <input type="date" id="cal-date" value="${today}" min="2026-01-01" max="2029-12-31">
    <button class="btn" id="cal-next">Tomorrow ▶</button>
    <button class="btn" id="cal-today">Today</button>
  </div><div class="small">Day status is evidence-aware: season ranges are caution windows, not proof of a game every day. Specific events with a start time get an estimated end using the duration model; missing schedules prevent a “verified free” claim.</div>`;
  function draw(){
    const d=byId('cal-date').value;
    const ws=windowsCoveringDate(d);
    const ev=eventsOnDate(d);
    const intervals=[];
    const unresolved=[];
    ev.forEach(e=>{
      if(/^\d{2}:\d{2}$/.test(e.time||'') && Number.isFinite(Number(e.endEstimateMin))){
        const [hh,mm]=e.time.split(':').map(Number);
        const start=hh*60+mm;
        intervals.push({start,end:start+Number(e.endEstimateMin),event:e});
      } else unresolved.push(e);
    });
    intervals.sort((a,b)=>a.start-b.start);
    const merged=[];
    intervals.forEach(i=>{
      const last=merged[merged.length-1];
      if(last && i.start<=last.end){last.end=Math.max(last.end,i.end);last.events.push(i.event);}
      else merged.push({start:i.start,end:i.end,events:[i.event]});
    });
    const hasEstimatedSeason=ws.some(w=>w.verification!=='verified');
    const status=ws.length?'IN LEAGUE WINDOW — CHECK SCHEDULE':(ev.length?'SCHEDULED EVENT(S) FOUND':'NO MODELED CONFLICT FOUND — NOT VERIFIED FREE');
    const statusClass=ws.length||ev.length?'b-busy':'b-unverified';
    let html=`<div class="cal-day"><h3>${fmtDate(d)} <span class="badge ${statusClass}">${status}</span></h3>`;
    if(ws.length){
      html+=`<div class="danger"><strong>Season-window caution:</strong> one or more modeled seasons overlap this date. This is not proof that a game is scheduled today, and the schedule coverage is incomplete; exact hourly free intervals cannot be certified from the current dataset.</div>`;
      ws.forEach(w=>{html+=`<div class="event ${w.priority==='high'?'high':''}"><div><strong>${esc(w.label)}</strong> ${prio(w.priority)} ${badge(w.verification)}</div><div class="meta">${esc(w.start)} to ${esc(w.end)} · ${esc(w.scope)} · Sources: ${srcLinks(w.sourceIds)}</div><div class="small">${esc(w.notes||'')}</div></div>`;});
    } else if(!ev.length){
      html+=`<div class="warn"><strong>No blocking event/window was found in the collected data for this day.</strong> This is not a verified free day: complete local radio, MLB, NFL and Stanford/Cal schedules are not present.</div>`;
    }
    if(ev.length){
      html+=`<h4>Specific events on record</h4>`;
      ev.forEach(e=>{
        const timeKnown=/^\d{2}:\d{2}$/.test(e.time||'');
        let timing=timeKnown?`${esc(e.time)} ${esc(e.tz||'PT')} — estimated end ${clockText(Number(e.time.slice(0,2))*60+Number(e.time.slice(3,5))+Number(e.endEstimateMin||0))} PT (${e.endEstimateMin} min assumed)`:'Start time not confirmed; treat event timing as unresolved.';
        html+=`<div class="event ${e.priority==='high'?'high':''}"><div><strong>${timing}</strong> — ${esc(e.teams)} ${prio(e.priority)} ${badge(e.verification)}</div><div class="meta">${esc(e.sport)} · Radio: ${esc(e.radio||'TBD')} · Sources: ${srcLinks(e.sourceIds)}</div><div class="small">${esc(e.notes||'')}</div></div>`;
      });
      if(merged.length && !ws.length){
        let cursor=0;
        html+=`<div class="note"><strong>Potential intervals outside the specific event(s) entered</strong> (PST; based only on collected events, not a complete schedule):<ul class="clean">`;
        merged.forEach(i=>{if(i.start>cursor)html+=`<li>${clockText(cursor)}–${clockText(i.start)} potentially clear of entered events</li>`;cursor=Math.max(cursor,i.end);});
        if(cursor<1440)html+=`<li>${clockText(cursor)}–24:00 potentially clear of entered events</li>`;
        html+=`</ul></div>`;
      }
    }
    if(hasEstimatedSeason) html+=`<div class="small">At least one overlapping season range is ESTIMATED. It is intentionally treated as a conservative caution window in vacation calculations.</div>`;
    const runs=findFreeRuns(d, addDays(d,60), 3);
    if(runs.length){html+=`<div style="margin-top:10px"><strong>Next 3+ day candidate runs (model only):</strong><ul class="clean">`+runs.slice(0,5).map(r=>`<li>${r.start} to ${r.end} (${r.days} days) ${badge('estimated')}</li>`).join('')+`</ul><div class="small">These runs are model outputs, not verified conflict-free periods.</div></div>`;}
    html+=`</div>`;
    el.innerHTML=html;
  }
  byId('cal-prev').onclick=()=>{const i=byId('cal-date'); i.value=addDays(i.value,-1); draw();};
  byId('cal-next').onclick=()=>{const i=byId('cal-date'); i.value=addDays(i.value,1); draw();};
  byId('cal-today').onclick=()=>{byId('cal-date').value=today; draw();};
  byId('cal-date').onchange=draw;
  draw();
}
window.addEventListener('DOMContentLoaded',()=>{
  renderSourcesTable('sources-table');
  renderEventsTable('events-table');
  renderWindowsTable('windows-table');
  renderCalendar('calendar-view','calendar-controls');
  const yearEl=byId('vac-year');
  if(yearEl){const go=()=>renderVacation('vacation-results',Number(yearEl.value));yearEl.onchange=go;go();}
  const summary=byId('summary-vacations'); if(summary){summary.innerHTML='<div class="small">For date-run detail, open <a href="vacation.html">Vacation Windows</a>. All future-year runs inherit estimated season-window uncertainty.</div>';}
  const teams=byId('teams-table'); if(teams){teams.innerHTML='<div class="table-wrap"><table><thead><tr><th>Club</th><th>Priority</th><th>Schedule evidence</th></tr></thead><tbody>'+MLB_TEAMS.map(t=>`<tr><td>${esc(t)}</td><td>${['San Francisco Giants','Athletics'].includes(t)?prio('high'):prio('normal')}</td><td>${['San Francisco Giants','Athletics'].includes(t)?'<a href="'+(t==='San Francisco Giants'?'https://www.mlb.com/giants/schedule':'https://www.mlb.com/athletics/schedule')+'" target="_blank" rel="noopener">Official team schedule</a>':'<span class="badge b-unverified">No individual rows collected</span> <a href="https://www.mlb.com/schedule" target="_blank" rel="noopener">Official MLB schedule hub</a>'}</td></tr>`).join('')+'</tbody></table></div>';}
});
