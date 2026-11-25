/* FREE TIME VACATION — shared helpers for docs/ pages */
export const NAV = [
  ['../index.html','Planner'],['index.html','Dashboard'],['executive-summary.html','Executive Summary'],
  ['windows.html','Vacation Windows'],['calendar.html','Scoreboard Calendar'],['mlb.html','MLB · All 30 Clubs'],
  ['nfl.html','NFL'],['ncaaf.html','NCAAF · Stanford & Cal'],['westwood.html','Westwood One Radio'],
  ['radio.html','AM/FM 94122'],['live-planner.html','Live MLB Feed'],['sources.html','Sources'],['methodology.html','Methodology'],['flagged.html','Flagged for Review'],
];
export function injectNav(active){
  const nav = document.querySelector('nav[data-site-nav]');
  if(!nav) return;
  nav.innerHTML = NAV.map(([href,label])=>{
    const cur = label===active ? ' aria-current="page"' : '';
    return `<a href="${href}"${cur}>${label}</a>`;
  }).join('');
}
export const esc = x => String(x ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const cache = new Map();
export async function loadYear(year){
  if(!cache.has(year)){
    cache.set(year, fetch(`../data/games-${year}.json`).then(r=>{ if(!r.ok) throw new Error('load failed '+year); return r.json(); }));
  }
  return cache.get(year);
}
let allCache = null;
export async function loadAll(){
  if(!allCache){
    allCache = Promise.all([2026,2027,2028,2029].map(y => loadYear(y))).then(parts => parts.flat());
  }
  return allCache;
}
let analysisCache = null;
export async function loadAnalysis(){
  if(!analysisCache){
    analysisCache = fetch('../data/vacation_analysis.json').then(r=>r.json());
  }
  return analysisCache;
}
let metaCache = null;
export async function loadMeta(){
  if(!metaCache){ metaCache = fetch('../data/meta.json').then(r=>r.json()); }
  return metaCache;
}
export function toMin(t){
  if(!t) return null;
  const [h,m] = t.split(':').map(Number);
  return h*60 + m;
}
export function clockPt(mins){
  mins = ((mins % 1440) + 1440) % 1440;
  let h = Math.floor(mins/60), m = mins%60;
  const ampm = h < 12 ? 'AM' : 'PM';
  return `${h%12||12}:${String(m).padStart(2,'0')} ${ampm}`;
}
export function mergeIntervals(iv){
  const out = [];
  for(const [s,e] of [...iv].sort((a,b)=>a[0]-b[0])){
    const ee = Math.min(e,1440);
    if(out.length && s <= out[out.length-1][1]) out[out.length-1][1] = Math.max(out[out.length-1][1], ee);
    else out.push([s,ee]);
  }
  return out;
}
export function dayIntervals(rows, date, mode){
  const out = [];
  for(const r of rows){
    if(r.date !== date) continue;
    if(/\(informational\)/.test(r.league)) continue;
    if(!['spring_training','preseason','regular','postseason','all_star','bowl'].includes(r.season_type)) continue;
    if(mode === 'practical' && r.priority !== 'high') continue;
    const s = toMin(r.start);
    out.push(s === null ? null : [s, s + r.minutes]);
  }
  return out;
}
export function freeWindows(intervals){
  const busy = mergeIntervals(intervals.filter(Boolean));
  const gaps = []; let cur = 0;
  for(const [s,e] of busy){ if(s > cur) gaps.push([cur,s]); cur = Math.max(cur, e); }
  if(cur < 1440) gaps.push([cur, 1440]);
  return {busy, gaps};
}
export function fmtDateLong(iso){
  const d = new Date(iso + 'T12:00:00');
  return d.toLocaleDateString('en-US', {weekday:'long', year:'numeric', month:'long', day:'numeric'});
}
export function fmtDateShort(iso){
  const d = new Date(iso + 'T12:00:00');
  return d.toLocaleDateString('en-US', {month:'short', day:'numeric', year:'numeric'});
}
export function monthName(y, m){ return new Date(y, m, 1).toLocaleDateString('en-US', {month:'long', year:'numeric'}); }
export function downloadCsv(filename, rows){
  const csv = rows.map(r => r.map(c => {
    const s = String(c ?? '');
    return /[",\n]/.test(s) ? '"' + s.replace(/"/g,'""') + '"' : s;
  }).join(',')).join('\n');
  const blob = new Blob([csv], {type:'text/csv;charset=utf-8'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = filename; a.click();
  URL.revokeObjectURL(a.href);
}
export function seasonTypeLabel(t){
  return {spring_training:'Spring Training', preseason:'Preseason', regular:'Regular season',
          postseason:'Postseason', all_star:'All-Star', bowl:'Bowl', conference_championship:'Conference championship'}[t] || t;
}
