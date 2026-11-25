import json, pathlib
root = pathlib.Path("docs")
(root/"assets").mkdir(parents=True, exist_ok=True)
sources = json.load(open("data/sources.json"))["sources"]
sched = json.load(open("data/schedules_2026.json"))
windows = json.load(open("data/windows_2026_2029.json"))

CSS = """*{box-sizing:border-box}body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f6f7f9;color:#1a1a1a;line-height:1.5}
header{background:#0b2a4a;color:#fff;padding:14px 20px}header a{color:#fff;text-decoration:none;font-weight:700;font-size:20px}
nav{background:#123a63;padding:8px 20px}nav a{color:#dbeafe;margin-right:14px;text-decoration:none}nav a:hover{text-decoration:underline}
main{max-width:1100px;margin:0 auto;padding:20px}h1,h2{color:#0b2a4a}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:16px;margin:14px 0}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{border:1px solid #e2e8f0;padding:6px 8px;text-align:left;vertical-align:top}
th{background:#eef2f7}.badge{display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:700}
.verified{background:#dcfce7;color:#166534}.estimated{background:#fef9c3;color:#854d0e}.flagged{background:#fee2e2;color:#991b1b}.partial{background:#e0e7ff;color:#3730a3}
.free{background:#dcfce7}.busy{background:#fee2e2}.gameday{background:#fef9c3}
.cal{display:grid;grid-template-columns:repeat(7,1fr);gap:4px}.cal div{border:1px solid #e2e8f0;border-radius:6px;padding:6px;font-size:13px;min-height:56px;background:#fff}
.cal .sel{outline:3px solid #2563eb}.cal button{width:100%;text-align:left;background:none;border:none;cursor:pointer;font:inherit}
.btn{background:#2563eb;color:#fff;border:none;border-radius:8px;padding:8px 14px;cursor:pointer;margin:2px}
.btn.secondary{background:#fff;color:#0b2a4a;border:1px solid #cbd5e1}
.small{font-size:13px;color:#475569}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}
footer{padding:20px;text-align:center;color:#64748b;font-size:13px}
a{color:#1d4ed8}"""

BLOCKS = [
 ("2026-02-20","2026-03-24","MLB Spring Training (all 30 clubs)","VERIFIED"),
 ("2026-03-25","2026-10-31","MLB regular season + postseason (all 30 clubs)","VERIFIED*"),
 ("2026-08-13","2027-02-08","NFL preseason + regular season + playoffs + Super Bowl LX","VERIFIED*"),
 ("2026-08-29","2027-01-25","NCAAF Stanford/Cal + bowls/CFP","VERIFIED"),
 ("2027-02-19","2027-03-24","MLB Spring Training (ESTIMATED start; verified end)","ESTIMATED"),
 ("2027-03-25","2027-10-31","MLB regular season + postseason","VERIFIED/ESTIMATED"),
 ("2027-08-01","2028-02-13","NFL season + Super Bowl LXII (ESTIMATED)","ESTIMATED"),
 ("2027-08-28","2028-01-24","NCAAF Stanford/Cal + bowls/CFP (ESTIMATED)","ESTIMATED"),
 ("2028-02-18","2028-03-23","MLB Spring Training (ESTIMATED)","ESTIMATED"),
 ("2028-03-24","2028-10-31","MLB regular season + postseason (ESTIMATED)","ESTIMATED"),
 ("2028-08-01","2029-02-11","NFL season + Super Bowl LXIII (ESTIMATED)","ESTIMATED"),
 ("2028-08-26","2029-01-22","NCAAF Stanford/Cal + bowls/CFP (ESTIMATED)","ESTIMATED"),
 ("2029-02-16","2029-03-21","MLB Spring Training (ESTIMATED)","ESTIMATED"),
 ("2029-03-22","2029-10-31","MLB regular season + postseason (ESTIMATED)","ESTIMATED"),
 ("2029-08-01","2030-02-10","NFL season + Super Bowl LXIV (ESTIMATED)","ESTIMATED"),
 ("2029-08-25","2030-01-21","NCAAF Stanford/Cal + bowls/CFP (ESTIMATED)","ESTIMATED"),
]
# game days 2026: date -> list
GAMES = {}
def add(date, time, label, dur):
    GAMES.setdefault(date, []).append({"time":time,"label":label,"dur":dur})
for g in sched["forty_niners_2026_regular"]:
    if g["date"]: add(g["date"], g["time_pt"], f"49ers {g['opponent']}", 192)
for g in sched["stanford_2026"]:
    add(g["date"], g["time"], f"Stanford vs {g['opponent']}", 204)
for g in sched["cal_2026"]:
    add(g["date"], g["time"], f"Cal vs {g['opponent']}", 204)
# Westwood One named 2026 games (subset of NFL dates; times ET -> PT approx -3h; store as published ET label)
WWO = [("2026-11-25","7:30 PM ET","Westwood One: Packers at Rams (Thanksgiving Wed)"),("2026-11-26","12:30 PM ET","Westwood One: Bears at Lions (Thanksgiving)"),("2026-11-26","4:15 PM ET","Westwood One: Eagles at Cowboys (Thanksgiving)"),("2026-11-26","8:00 PM ET","Westwood One: Chiefs at Bills (Thanksgiving)"),("2026-11-27","2:30 PM ET","Westwood One: Broncos at Steelers (Black Friday)"),("2026-11-30","7:00 PM ET","Westwood One: Panthers at Buccaneers (MNF)"),("2026-12-06","7:30 PM ET","Westwood One: Texans at Steelers (SNF)"),("2026-12-10","7:30 PM ET","Westwood One: Vikings at Patriots (TNF)"),("2026-12-14","7:00 PM ET","Westwood One: Steelers at Jaguars (MNF)"),("2026-12-17","7:30 PM ET","Westwood One: 49ers at Chargers (TNF)"),("2026-12-20","7:30 PM ET","Westwood One: Lions at Vikings (SNF)"),("2026-12-24","7:30 PM ET","Westwood One: Texans at Eagles (TNF)"),("2026-12-25","12:30 PM ET","Westwood One: Packers at Bears (Christmas)"),("2026-12-25","4:15 PM ET","Westwood One: Bills at Broncos (Christmas)"),("2026-12-25","8:00 PM ET","Westwood One: Rams at Seahawks (Christmas)"),("2026-12-27","7:30 PM ET","Westwood One: Jaguars at Cowboys (SNF)"),("2026-12-31","7:30 PM ET","Westwood One: Ravens at Bengals (TNF)"),("2027-01-03","7:30 PM ET","Westwood One: Eagles at 49ers (SNF)"),("2027-01-04","7:00 PM ET","Westwood One: Texans at Packers (MNF)")]
for d,t,l in WWO: add(d,t,l,192)

JS = "const BLOCKS="+json.dumps(BLOCKS)+";\nconst GAMES="+json.dumps(GAMES)+";\n"
JS += r"""
const $=id=>document.getElementById(id);
function parse(d){return new Date(d+"T12:00:00");}
function fmt(d){return d.toISOString().slice(0,10);}
function addDays(d,n){const x=new Date(d);x.setDate(x.getDate()+n);return x;}
function blocksOn(date){return BLOCKS.filter(b=>date>=b[0]&&date<=b[1]);}
function status(date){const b=blocksOn(date);const g=GAMES[date];if(b.length)return "BUSY";if(g&&g.length)return "GAME DAY";return "FREE";}
function renderDay(){
  const date=$("dateInput").value; if(!date)return;
  const st=status(date); const b=blocksOn(date); const g=GAMES[date]||[];
  let h="<h2>"+date+" — "+st+"</h2>";
  if(b.length){h+="<p><strong>Busy blocks:</strong></p><ul>"+b.map(x=>"<li>"+x[2]+" ("+x[0]+" to "+x[1]+") ["+x[3]+"]</li>").join("")+"</ul>";}
  if(g.length){h+="<p><strong>Verified 2026 games (PT unless ET noted):</strong></p><table><tr><th>Start</th><th>Game</th><th>Avg duration</th><th>Expected end*</th></tr>"+g.map(x=>"<li></li>").join("")+"</table>";
    h="<h2>"+date+" — "+st+"</h2>"+(b.length?"<p><strong>Busy blocks:</strong></p><ul>"+b.map(x=>"<li>"+x[2]+" ("+x[0]+" to "+x[1]+") ["+x[3]+"]</li>").join("")+"</ul>":"")+"<p><strong>Verified 2026 games:</strong></p><table><tr><th>Start</th><th>Game</th><th>Avg duration</th><th>Expected end*</th></tr>"+g.map(x=>{let end="—";const m=x.time.match(/(\d+):(\d+)\s*(AM|PM)/);if(m){let hh=+m[1]%12;if(m[3]==="PM")hh+=12;const mins=hh*60+(+m[2])+x.dur;end=String(Math.floor(mins/60)%24).padStart(2,"0")+":"+String(mins%60).padStart(2,"0");}return "<tr><td>"+x.time+"</td><td>"+x.label+"</td><td>"+x.dur+" min</td><td>~"+end+"</td></tr>";}).join("")+"</table><p class='small'>*Expected end = start + average duration. Actual end varies (OT, delays, extra innings). Free time = minutes outside all game blocks. On full-block days (MLB/NFL/NCAAF season spans), treat the whole date as NOT free for vacation purposes even if hourly gaps exist.</p>";
  } else if(!b.length){h+="<p>✅ No in-scope season block or verified game on this date. Under the strict definition this date is FREE (subject to estimated-block caveats for 2027-2029).</p>";}
  else {h+="<p>⛔ In-scope season block covers this date — NOT free for vacation. See hourly detail only if specific verified games are listed above.</p>";}
  $("dayDetail").innerHTML=h;
  renderCal();
}
function renderCal(){
  const v=$("dateInput").value; if(!v)return; const d=parse(v); const y=d.getFullYear(), m=d.getMonth();
  const first=new Date(y,m,1); const startDay=first.getDay(); const days=new Date(y,m+1,0).getDate();
  let h="<div class='cal'>";
  for(let i=0;i<startDay;i++)h+="<div></div>";
  for(let day=1;day<=days;day++){const ds=fmt(new Date(y,m,day));const st=status(ds);const cls=st==="FREE"?"free":st==="BUSY"?"busy":"gameday";const sel=ds===v?" sel":"";
    h+="<div class='"+cls+sel+"'><button onclick=\"document.getElementById('dateInput').value='"+ds+"';renderDay();\">"+day+"<br><small>"+st+"</small></button></div>";}
  h+="</div>"; $("cal").innerHTML=h;
}
function step(n){const v=$("dateInput").value;if(!v)return;const d=addDays(parse(v),n);$("dateInput").value=fmt(d);renderDay();}
document.addEventListener("DOMContentLoaded",()=>{const t=new Date();$("dateInput").value=fmt(t);renderDay();});
"""

def page(title, body):
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} | Freetime2</title><link rel="stylesheet" href="assets/style.css"></head><body>
<header><a href="index.html">Freetime2 — Bay Area Sports Radio Free-Time Planner</a></header>
<nav><a href="index.html">Dashboard</a><a href="executive-summary.html">Executive Summary</a><a href="windows.html">Vacation Windows</a><a href="schedules.html">2026 Schedules</a><a href="radio.html">Bay Area Radio</a><a href="methodology.html">Methodology & Day Planner</a><a href="flagged.html">Flagged for Review</a></nav>
<main>{body}</main><footer>Freetime2 • Times in PT (America/Los_Angeles) unless noted • ESTIMATED blocks are not confirmed schedules • See <a href="flagged.html">Flagged for Review</a></footer></body></html>"""

# tables
def sched_table(rows, cols):
    h="<table><tr>"+"".join(f"<th>{c}</th>" for c in cols)+"</tr>"
    for r in rows:
        h+="<tr>"+"".join(f"<td>{r.get(c,'')}</td>" for c in cols)+"</tr>"
    return h+"</table>"

src_rows = [{"id":s["id"],"title":s["title"],"publisher":s["publisher"],"covers":s["covers"],"status":s["status"],"link":f'<a href="{s["url"]}" target="_blank" rel="noopener">Open</a>'} for s in sources]

index_body = f"""<h1>Dashboard — When are you free?</h1>
<div class="card"><p><strong>Question:</strong> When is the best time to take a vacation from Outer Sunset (94122) without missing live sports you would stay home to hear on AM/FM radio?</p>
<p><strong>Short answer:</strong> Under the strict definition (any of all 30 MLB clubs incl. Spring Training, any NFL game, Stanford/Cal, Westwood One national), the only multi-day gap each year is a <strong>short February window between the Super Bowl and Spring Training</strong> — about <strong>11 days in 2026 (Feb 9–19)</strong> and only <strong>~4 days in 2027–2029 (estimated)</strong>. A true 2–3 week vacation requires the <strong>practical definition</strong> (Giants/A's/49ers/Stanford/Cal/Westwood One only, ignoring other clubs' Spring Training): <strong>mid-February to late March</strong>. See <a href="windows.html">Vacation Windows</a>.</p>
<p><span class="badge verified">VERIFIED</span> = official source &nbsp; <span class="badge estimated">ESTIMATED</span> = pattern-based, not released &nbsp; <span class="badge flagged">FLAGGED</span> = unverified, do not rely on</p></div>
<div class="card"><h2>Quick links</h2><div class="grid">
<div><h3>Executive Summary</h3><p>One-page brief for planning.</p><p><a href="executive-summary.html">Open →</a></p></div>
<div><h3>Vacation Windows 2026–2029</h3><p>Strict vs practical windows with sources.</p><p><a href="windows.html">Open →</a></p></div>
<div><h3>2026 Schedules</h3><p>49ers, Stanford, Cal game tables.</p><p><a href="schedules.html">Open →</a></p></div>
<div><h3>Bay Area Radio</h3><p>KNBR/Westwood One + other stations.</p><p><a href="radio.html">Open →</a></p></div>
<div><h3>Day Planner</h3><p>Pick any day; see free/busy + hourly math.</p><p><a href="methodology.html">Open →</a></p></div>
<div><h3>Flagged for Review</h3><p>Unverified items + irregularities.</p><p><a href="flagged.html">Open →</a></p></div>
</div></div>
<div class="card"><h2>Source registry (official first)</h2>{sched_table(src_rows,["id","title","publisher","covers","status","link"])}</div>"""

exec_body = """<h1>Executive Summary</h1>
<div class="card"><h2>Bottom line</h2><p>There is <strong>no 2–3 week fully-free window</strong> under the strict all-30-clubs definition. MLB (Spring Training Feb–Mar through postseason Oct), NFL (preseason Aug through Super Bowl Feb), and Stanford/Cal NCAAF (late Aug through bowls/CFP Jan) overlap or abut almost year-round. The <strong>only strict gap is in February</strong> between the Super Bowl and Spring Training.</p></div>
<div class="card"><h2>Best vacation candidates</h2><table><tr><th>Year</th><th>Strict (all 30 MLB incl. Spring Training)</th><th>Practical (Bay Area teams + Westwood One only)</th><th>Status</th></tr>
<tr><td>2026</td><td>Feb 9–19 (11 days)</td><td>Feb 9–Mar 24 (44 days)</td><td><span class="badge verified">VERIFIED boundaries</span></td></tr>
<tr><td>2027</td><td>Feb 15–18 (~4 days)</td><td>Feb 15–Mar 24 (38 days)</td><td><span class="badge partial">MIXED</span> Opening Day verified; Spring Training start estimated</td></tr>
<tr><td>2028</td><td>Feb 14–17 (~4 days)</td><td>Feb 14–~Mar 23 (~39 days)</td><td><span class="badge estimated">ESTIMATED</span></td></tr>
<tr><td>2029</td><td>Feb 12–15 (~4 days)</td><td>Feb 12–~Mar 22 (~39 days)</td><td><span class="badge estimated">ESTIMATED</span></td></tr></table>
<p class="small">Practical windows still contain Giants/Athletics Spring Training games — check club Spring Training schedules before booking. Do not book non-refundable travel on ESTIMATED years.</p></div>
<div class="card"><h2>What counts as busy</h2><ul><li><strong>MLB:</strong> Giants + Athletics (high priority) + all 30 clubs, Spring Training through World Series.</li><li><strong>NFL:</strong> 49ers (high priority) + all NFL games; Westwood One national radio games are a subset of NFL dates.</li><li><strong>NCAAF:</strong> Stanford + Cal (high priority), regular season through bowls/CFP.</li><li><strong>Radio:</strong> KNBR 680 AM / 104.5 FM (Westwood One Sports affiliate) is the primary Bay Area outlet; see Radio page for others.</li></ul></div>
<div class="card"><h2>Daily free time</h2><p>On game days, free hours = before first game / between games / after last game (PT), using researched averages: MLB ~170 min, NFL ~192 min, NCAAF ~204 min. Example: 1:05 PM PT NFL kickoff → ~4:17 PM PT expected end. Use the Day Planner for exact math per date.</p></div>"""

win_rows = ""
for w in windows["windows"]:
    win_rows += f"<tr><td>{w['id']}<br>{w['label']}</td><td>{w['strict']['start']} to {w['strict']['end']} ({w['strict']['days']}d)<br><small>{w['strict']['why']}</small></td><td>{w['practical']['start']} to {w['practical']['end']} ({w['practical']['days']}d)<br><small>{w['practical']['why']}</small></td><td>{w['status']}<br><small>Sources: {', '.join(w['sources'])}</small></td></tr>"
windows_body = f"""<h1>Vacation Windows 2026–2029</h1>
<div class="card"><p><strong>Strict</strong> = all 30 MLB clubs incl. Spring Training count. <strong>Practical</strong> = only Giants/A's/49ers/Stanford/Cal/Westwood One count. ESTIMATED = no official schedule released; pattern-based only.</p>
<table><tr><th>Window</th><th>Strict</th><th>Practical</th><th>Status / Sources</th></tr>{win_rows}</table></div>
<div class="card"><h2>Busy blocks (strict)</h2><table><tr><th>Start</th><th>End</th><th>Block</th><th>Status</th></tr>{''.join(f'<tr><td>{b[0]}</td><td>{b[1]}</td><td>{b[2]}</td><td>{b[3]}</td></tr>' for b in BLOCKS)}</table>
<p class="small">*VERIFIED* = start/end bounded by official releases (see Sources). 2027–2029 NFL/NCAAF/MLB game-by-game schedules were not released at build time; blocks are ESTIMATED from official season-structure patterns. Re-verify when leagues release schedules.</p></div>"""

s49 = sched_table(sched["forty_niners_2026_regular"], ["week","date","day","opponent","time_pt","source"])
sst = sched_table(sched["stanford_2026"], ["date","opponent","time","source"])
scal = sched_table(sched["cal_2026"], ["date","opponent","time","source"])
sched_body = f"""<h1>2026 Schedules (verified rows)</h1>
<div class="card"><h2>San Francisco 49ers — 2026 regular season</h2>{s49}<p class="small">Source: 49ers.com/schedule/. Week 18 TBD is flagged unverified — see Flagged page. Preseason dates in data file are secondary-only and flagged.</p></div>
<div class="card"><h2>Stanford Cardinal — 2026</h2>{sst}<p class="small">Source: gostanford.com/sports/football/schedule.</p></div>
<div class="card"><h2>California Golden Bears — 2026</h2>{scal}<p class="small">Source: calbears.com/sports/football/schedule/text.</p></div>
<div class="card"><h2>MLB boundaries</h2><p>2026: Spring Training Feb 20; Opening Night Mar 25 (Giants vs Yankees); Opening Day Mar 26; Athletics Mar 27. 2027: Opening Day Mar 25 (verified via MLB club releases); final series Sep 24–26. Full game-by-game MLB tables require per-team MLB.com schedule pages — season boundaries are recorded here; individual game rows are not fabricated.</p></div>
<div class="card"><h2>Westwood One national NFL radio (2026, selected)</h2><p>See Radio page for the named 2026 slate with event links. Westwood One carries selected primetime/holiday games, not every NFL game — but every Westwood One date is also an NFL date, so it never extends a busy block.</p></div>"""

radio_body = """<h1>Bay Area Radio — What you can hear on AM/FM in 94122</h1>
<div class="card"><h2>Primary: KNBR 680 AM / 104.5 FM — The Sports Leader (San Francisco)</h2><ul><li><strong>KNBR 680 AM</strong> (50,000-watt clear-channel, Redwood City transmitter) + <strong>KNBR-FM 104.5</strong> simulcast (Sutro Tower) — both receivable on a standard AM/FM radio in Outer Sunset.</li><li><strong>Westwood One Sports affiliate</strong> — carries Westwood One national NFL radio (TNF/MNF/SNF, holiday tripleheaders, playoffs, Super Bowl).</li><li><strong>Giants Radio Network flagship</strong> (since 1979) and <strong>49ers Radio Network co-flagship</strong> (with KSAN/KSFO); also Stanford Cardinal radio home per station materials.</li><li>Official programming/schedule: <a href="https://www.thesportsleader.com/shows/" target="_blank" rel="noopener">thesportsleader.com/shows</a> • Westwood One NFL schedule: <a href="https://www.westwoodonesports.com/nfl-schedule/" target="_blank" rel="noopener">westwoodonesports.com/nfl-schedule</a></li></ul></div>
<div class="card"><h2>Westwood One 2026 NFL national radio slate (named games, ET)</h2><table><tr><th>Date</th><th>Time (ET)</th><th>Game</th></tr>""" + "".join(f"<tr><td>{d}</td><td>{t}</td><td>{l}</td></tr>" for d,t,l in WWO) + """</table><p class="small">Source: westwoodonesports.com/nfl-schedule/ (event pages linked there). TBA slots (Weeks 16–18) are flagged, not filled in. Convert ET→PT (−3h) for Outer Sunset listening.</p></div>
<div class="card"><h2>Other Bay Area sports radio (flagged additional risks — outside core definition)</h2><ul><li><strong>KTCT 1050 AM</strong> (KNBR sister, ESPN Radio) — overflow for KNBR conflicts.</li><li><strong>KSAN / KSFO</strong> — 49ers co-flagship outlets.</li><li><strong>KGMZ 95.7 FM The Game</strong> (Audacy) — Warriors/Sharks and other sports; <em>not</em> Westwood One. If you count NBA/NHL, free time shrinks further — flagged for your review, not in core windows.</li><li><strong>Westwood One other properties</strong> (NCAA basketball, golf, U.S. Soccer, NCAA baseball/softball, etc.) — listed on westwoodonesports.com; outside core NFL/MLB/NCAAF definition but could affect listening. Flagged for review.</li></ul><p class="small">Rule used: a game is "on the radio" if its league/team is in scope AND it is carried by KNBR/Westwood One or the team network. Westwood One dates are a subset of NFL dates.</p></div>"""

meth_body = """<h1>Methodology & Day Planner</h1>
<div class="card"><h2>How free time is calculated</h2><ol><li>Mark season blocks busy (MLB Spring Training→World Series; NFL preseason→Super Bowl; NCAAF regular season→CFP title).</li><li>For specific verified game dates, add game blocks: start time + average duration.</li><li>Free = minutes outside all blocks (PT). For vacation purposes, any date inside a season block = NOT free, even if hourly gaps exist.</li></ol>
<h3>Average durations (researched, not user guesses)</h3><table><tr><th>Sport</th><th>Avg real-time duration</th><th>Halftime</th><th>Notes</th></tr>
<tr><td>MLB regular season</td><td>~170 min (2h50m)</td><td>—</td><td>2024 pitch-clock era; postseason ~185 min</td></tr>
<tr><td>NFL</td><td>~192 min (3h12m)</td><td>~12 min</td><td>60-min clock; range ~3h02m–3h12m</td></tr>
<tr><td>NCAAF</td><td>~204 min (3h24m)</td><td>~20 min</td><td>Longer than NFL (clock rules + halftime)</td></tr></table>
<p class="small">Your suggested 150/180-min figures understate current averages; the planner uses researched values. Add pregame/postgame buffers separately if you want conservative estimates.</p></div>
<div class="card"><h2>Day Planner — pick any day (PT)</h2>
<p><button class="btn" onclick="step(-1)">← Yesterday</button> <button class="btn" onclick="step(1)">Tomorrow →</button> <input type="date" id="dateInput"> <button class="btn secondary" onclick="renderDay()">Go</button></p>
<div id="dayDetail"></div><h3>Month calendar (click a day)</h3><div id="cal"></div>
<p class="small">Calendar colors: green=FREE, red=BUSY (season block), yellow=GAME DAY (specific verified game). 2027–2029 blocks are ESTIMATED — see Flagged page.</p></div>"""

flag_body = """<h1>Flagged for Review</h1>
<div class="card"><h2>Unverified items (do not rely on)</h2><ul>
<li>49ers Week 18 2026 opponent/date/time — TBD at fetch time.</li>
<li>49ers 2026 preseason times — secondary summary only.</li>
<li>Stanford/Cal 2026 times marked TBA at announcement — check official schedule pages for final times.</li>
<li>Pro Bowl Games 2026–2029 dates — not verified in this build.</li>
<li>All 2027–2029 NFL/NCAAF/MLB game-by-game schedules — not released; ESTIMATED blocks only.</li>
<li>Reference sites (VacationSchedule, ScheduleFreeTime, RADIOSF) — not fetchable in build environment; no data taken from them.</li></ul></div>
<div class="card"><h2>Irregularities</h2><ol>
<li><strong>Super Bowl LXI date conflict:</strong> Feb 14, 2027 (Wikipedia table + most secondaries) vs Feb 15, 2027 (one secondary). Site uses Feb 14. Resolve on NFL.com.</li>
<li><strong>MLB postseason end</strong> depends on series lengths (World Series Game 7 if needed Oct 31, 2026). Site shows full possible span as busy.</li>
<li><strong>Westwood One page</strong> shows duplicate Upcoming/Past listings + TBA Weeks 16–18 slots. Only named games recorded as verified.</li>
<li><strong>Duration inputs:</strong> user-suggested 150/180 min vs researched ~170/192/204 min. Site uses researched values.</li></ol>
<p>Full log: <a href="../VERIFICATION.md">VERIFICATION.md</a> in repo root. Flagged items do not block publishing; review after site is live and request changes.</p></div>"""

pages = {
 "index.html": page("Dashboard", index_body),
 "executive-summary.html": page("Executive Summary", exec_body),
 "windows.html": page("Vacation Windows", windows_body),
 "schedules.html": page("2026 Schedules", sched_body),
 "radio.html": page("Bay Area Radio", radio_body),
 "methodology.html": page("Methodology & Day Planner", meth_body),
 "flagged.html": page("Flagged for Review", flag_body),
}
for name, html in pages.items():
    (root/name).write_text(html)
(root/"assets"/"style.css").write_text(CSS)
(root/"assets"/"app.js").write_text(JS)
print("built", len(pages), "pages")
