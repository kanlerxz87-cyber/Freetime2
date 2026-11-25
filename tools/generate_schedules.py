#!/usr/bin/env python3
"""Free Time Vacation — schedule data generator (2026–2029).

Produces deterministic ESTIMATED game rows for all 30 MLB clubs, all NFL teams,
and Stanford/Cal NCAAF, anchored to the officially announced season boundaries
(which are encoded verbatim and tagged verified=True where confirmed official).

Nothing in this file should be read as a real, released schedule for
2027/2028/2029 — every generated row is tagged estimated=True. Only the
anchor events listed in VERIFIED_ANCHORS are officially confirmed.

Outputs (written to data/):
  games-2026.json ... games-2029.json  (array of game rows)
  vacation_analysis.json               (computed busy/free analysis per year)
  meta.json                            (build provenance)

Row schema:
  id, sport, league, season_type, date (YYYY-MM-DD), start ("HH:MM" PT 24h or null TBD),
  minutes (int), away, home, title, priority ("high"|"normal"),
  verified (bool), estimated (bool), flags (list), source (url), source_label, note
"""
import json, math, random, datetime, pathlib
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
TZ = "America/Los_Angeles"

DUR = {"MLB_regular": 158, "MLB_postseason": 185, "MLB_spring": 165, "MLB_allstar": 170,
       "NFL": 183, "NCAAF": 207, "WW1_EXTRA": 183}

def row(id_, sport, league, season_type, date, start, minutes, away, home,
        priority, verified, source, source_label, note="", flags=None):
    title = f"{away} at {home}" if away and home else (away or home or "Game")
    return {
        "id": id_, "sport": sport, "league": league, "season_type": season_type,
        "date": date, "start": start, "minutes": minutes,
        "away": away, "home": home, "title": title,
        "priority": priority, "verified": bool(verified), "estimated": not verified,
        "flags": flags or [], "source": source, "source_label": source_label, "note": note,
    }

def d_add(d, days): return (datetime.date.fromisoformat(d) + datetime.timedelta(days=days)).isoformat()
def d_parse(d): return datetime.date.fromisoformat(d)
def d_range(a, b):
    d, out = d_parse(a), []
    while d <= d_parse(b):
        out.append(d.isoformat()); d += datetime.timedelta(days=1)
    return out
def dow(d): return d_parse(d).strftime("%a")

# ----------------------------------------------------------------------------- MLB
MLB_TEAMS = [
    ("BAL","Baltimore Orioles","AL","East",110),("BOS","Boston Red Sox","AL","East",111),
    ("NYY","New York Yankees","AL","East",147),("TB","Tampa Bay Rays","AL","East",139),("TOR","Toronto Blue Jays","AL","East",141),
    ("CWS","Chicago White Sox","AL","Central",145),("CLE","Cleveland Guardians","AL","Central",114),("DET","Detroit Tigers","AL","Central",116),("KC","Kansas City Royals","AL","Central",118),("MIN","Minnesota Twins","AL","Central",142),
    ("HOU","Houston Astros","AL","West",117),("LAA","Los Angeles Angels","AL","West",108),("ATH","Athletics (Sacramento)","AL","West",133),("SEA","Seattle Mariners","AL","West",136),("TEX","Texas Rangers","AL","West",140),
    ("ATL","Atlanta Braves","NL","East",144),("MIA","Miami Marlins","NL","East",146),("NYM","New York Mets","NL","East",121),("PHI","Philadelphia Phillies","NL","East",143),("WSN","Washington Nationals","NL","East",120),
    ("CHC","Chicago Cubs","NL","Central",112),("CIN","Cincinnati Reds","NL","Central",113),("MIL","Milwaukee Brewers","NL","Central",158),("PIT","Pittsburgh Pirates","NL","Central",134),("STL","St. Louis Cardinals","NL","Central",138),
    ("AZ","Arizona Diamondbacks","NL","West",109),("COL","Colorado Rockies","NL","West",115),("LAD","Los Angeles Dodgers","NL","West",119),("SD","San Diego Padres","NL","West",135),("SF","San Francisco Giants","NL","West",137),
]
HIGH_MLB = {"SF","ATH"}           # high-priority clubs
MLB_BY_ABBR = {t[0]: t for t in MLB_TEAMS}

def mlb_pair_counts():
    """Balanced-format pairing: 13x division, 6/7 intra-league, 3/4 interleague. Deterministic."""
    pairs = defaultdict(int)
    # Division: 13 each
    for lg in ("AL","NL"):
        divs = defaultdict(list)
        for abbr,_,l,d,_ in MLB_TEAMS:
            if l == lg: divs[d].append(abbr)
        for d, clubs in divs.items():
            for i in range(len(clubs)):
                for j in range(i+1, len(clubs)):
                    pairs[tuple(sorted((clubs[i],clubs[j])))] = 13
    # Intra-league cross-division: base 6 + two perfect-match bumps per division-pair -> 64 avg
    for lg in ("AL","NL"):
        divs = defaultdict(list)
        for abbr,_,l,d,_ in MLB_TEAMS:
            if l == lg: divs[d].append(abbr)
        dnames = sorted(divs)
        for x in range(len(dnames)):
            for y in range(x+1, len(dnames)):
                A, B = divs[dnames[x]], divs[dnames[y]]
                for a in A:
                    for b in B:
                        pairs[tuple(sorted((a,b)))] = 6
                for s in (1,2):
                    for i in range(5):
                        pairs[tuple(sorted((A[i], B[(i+s) % 5])))] += 1
    # Interleague: base 3 each + one bijection bump -> 46 avg
    al = [t[0] for t in MLB_TEAMS if t[2]=="AL"]; nl = [t[0] for t in MLB_TEAMS if t[2]=="NL"]
    for a in al:
        for b in nl:
            pairs[tuple(sorted((a,b)))] = 3
    for i in range(15):
        pairs[tuple(sorted((al[i], nl[(7*i+3) % 15])))] += 1
    return pairs

def is_high_mlb(a, b):
    return (a[0] in HIGH_MLB) or (b[0] in HIGH_MLB)

def gen_mlb_games(year, opening_date, final_date, rng):
    """Greedy booking of all regular-season games onto dates; <=15 games/date cap."""
    pairs = mlb_pair_counts()
    days = d_range(opening_date, final_date)
    # weights: heavier Fri/Sat/Sun; light Mon/Wed
    w = {"Sat": 10, "Sun": 10, "Fri": 8, "Tue": 6, "Thu": 6, "Mon": 2, "Wed": 2}
    day_w = [(d, w[dow(d)]) for d in days]
    total_w = sum(x[1] for x in day_w)
    team_day = defaultdict(set); day_count = defaultdict(int)
    games = []
    queue = []
    for (a,b), n in pairs.items():
        queue += [(a,b)] * n
    rng.shuffle(queue)
    # Opening date & final date must carry full slates
    forced = {opening_date: 15}
    if final_date != opening_date: forced[final_date] = 15
    gi = 0
    for a,b in queue:
        booked = False
        # try up to 600 samples of weighted dates
        for _ in range(600):
            r = rng.random() * total_w; acc = 0; pick = days[-1]
            for d, weight in day_w:
                acc += weight
                if r <= acc: pick = d; break
            if day_count[pick] >= 15: continue
            if a in team_day[pick] or b in team_day[pick]: continue
            booked = True; break
        if not booked:
            # fall back: first date with capacity and both teams free
            for d in days:
                if day_count[d] < 15 and a not in team_day[d] and b not in team_day[d]:
                    pick = d; booked = True; break
        if not booked:
            continue  # extremely unlikely; would show as missing game -> flagged
        team_day[pick].add(a); team_day[pick].add(b); day_count[pick] += 1
        gi += 1
        # times: weekend day games / weekday nights
        dd = dow(pick)
        if dd == "Sun":
            slot = rng.choice(["12:35","1:05","1:05","1:35","4:05","5:10","5:20","7:10"])
        elif dd == "Sat":
            slot = rng.choice(["12:35","1:05","1:05","1:35","4:05","6:10","7:10","6:40"])
        else:
            slot = rng.choice(["1:05","1:35","4:05","6:40","7:05","7:05","7:10"])
        A, B = MLB_BY_ABBR[a], MLB_BY_ABBR[b]
        games.append(row(f"MLB-{year}-{gi:04d}", "MLB", "MLB", "regular", pick, slot,
                         DUR["MLB_regular"], A[1], B[1],
                         "high" if is_high_mlb(A,B) else "normal", False,
                         "https://www.mlb.com/schedule",
                         "MLB.com schedule (ESTIMATED reconstruction — see Flagged for Review)",
                         note="Estimated pairing/date/time. 2026 & 2027 master schedules are officially released but could not be machine-imported here; verify on MLB.com.",
                         flags=["estimated"]))
    return games

def gen_spring_training(year, start_date, end_date, rng):
    """Light exhibition model (~28 games/team) for busy-day estimation."""
    games = []; gi = 0
    days = d_range(start_date, end_date)
    day_w = [(d, {"Sat":10,"Sun":10,"Fri":8,"Tue":7,"Thu":7,"Wed":7,"Mon":4}[dow(d)]) for d in days]
    total_w = sum(x[1] for x in day_w)
    team_day = defaultdict(set); day_count = defaultdict(int)
    clubs = [t[0] for t in MLB_TEAMS]
    for _ in range(420):
        a, b = rng.choice(clubs), rng.choice(clubs)
        if a == b: continue
        pick = days[rng.randrange(len(days))]
        if day_count[pick] >= 15: continue
        if a in team_day[pick] or b in team_day[pick]: continue
        team_day[pick].add(a); team_day[pick].add(b); day_count[pick] += 1
        gi += 1
        slot = rng.choice(["11:05","12:05","1:05","1:05","4:05","6:05"])
        A, B = MLB_BY_ABBR[a], MLB_BY_ABBR[b]
        games.append(row(f"ST-{year}-{gi:03d}", "MLB", "MLB", "spring_training", pick, slot,
                         DUR["MLB_spring"], A[1], B[1],
                         "high" if is_high_mlb(A,B) else "normal", False,
                         "https://www.mlb.com/spring-training",
                         "MLB Spring Training (ESTIMATED — schedule not fully released/imported)",
                         note="Exhibition estimate for busy-day modelling.",
                         flags=["estimated","spring_training"]))
    return games

def gen_mlb_postseason(year, windows, rng):
    """windows: list of (date, games_on_date, label, verified)."""
    games = []; gi = 0
    for date, n, label, verified in windows:
        for k in range(n):
            gi += 1
            home, away = rng.choice(MLB_TEAMS), rng.choice(MLB_TEAMS)
            while away is home: away = rng.choice(MLB_TEAMS)
            slot = rng.choice(["17:30","17:08","13:08","20:08"])  # PT evening/afternoon
            games.append(row(f"POST-{year}-{gi:03d}", "MLB", "MLB", "postseason", date, slot,
                             DUR["MLB_postseason"], away[1], home[1], "normal", verified,
                             "https://www.mlb.com/postseason",
                             f"MLB Postseason {year} ({label})",
                             note="Matchup TBD — series in this window will be determined during the season.",
                             flags=["postseason"] + ([] if verified else ["estimated"])))
    return games

# ----------------------------------------------------------------------------- NFL
NFL_TEAMS = [
    ("ARI","Arizona Cardinals","NFC","West"),("ATL","Atlanta Falcons","NFC","South"),("BAL","Baltimore Ravens","AFC","North"),("BUF","Buffalo Bills","AFC","East"),
    ("CAR","Carolina Panthers","NFC","South"),("CHI","Chicago Bears","NFC","North"),("CIN","Cincinnati Bengals","AFC","North"),("CLE","Cleveland Browns","AFC","North"),
    ("DAL","Dallas Cowboys","NFC","East"),("DEN","Denver Broncos","AFC","West"),("DET","Detroit Lions","NFC","North"),("GB","Green Bay Packers","NFC","North"),
    ("HOU","Houston Texans","AFC","South"),("IND","Indianapolis Colts","AFC","South"),("JAX","Jacksonville Jaguars","AFC","South"),("KC","Kansas City Chiefs","AFC","West"),
    ("LAC","Los Angeles Chargers","AFC","West"),("LAR","Los Angeles Rams","NFC","West"),("LV","Las Vegas Raiders","AFC","West"),("MIA","Miami Dolphins","AFC","East"),
    ("MIN","Minnesota Vikings","NFC","North"),("NE","New England Patriots","AFC","East"),("NO","New Orleans Saints","NFC","South"),("NYG","New York Giants","NFC","East"),
    ("NYJ","New York Jets","AFC","East"),("PHI","Philadelphia Eagles","NFC","East"),("PIT","Pittsburgh Steelers","AFC","North"),("SEA","Seattle Seahawks","NFC","West"),
    ("SF","San Francisco 49ers","NFC","West"),("TB","Tampa Bay Buccaneers","NFC","South"),("TEN","Tennessee Titans","AFC","South"),("WAS","Washington Commanders","NFC","East"),
]
NFL_HIGH = {"SF"}
ALL_PAIRS = [tuple(sorted((a,b))) for i,(a,_,_,_) in enumerate(NFL_TEAMS) for b,_,_,_ in NFL_TEAMS[i+1:]]
DIV_PAIRS = set()
for (lg,d), clubs in defaultdict(list).items() or {}.items(): pass
_divs = defaultdict(list)
for a,_,lg,d in NFL_TEAMS: _divs[(lg,d)].append(a)
for clubs in _divs.values():
    for i in range(len(clubs)):
        for j in range(i+1, len(clubs)):
            DIV_PAIRS.add(tuple(sorted((clubs[i], clubs[j]))))

def gen_nfl(year, kickoff_date, rng):
    """272-game skeleton. Opponent allocation is a balanced random model flagged estimated."""
    teams = [t[0] for t in NFL_TEAMS]
    name = {t[0]: t[1] for t in NFL_TEAMS}
    pair_cap = {p: (2 if p in DIV_PAIRS else 1) for p in ALL_PAIRS}
    counts = defaultdict(int)
    kickoff = d_parse(kickoff_date)
    wd = kickoff.weekday()
    first_sunday = kickoff + datetime.timedelta(days=(6 - wd) % 7)
    games = []
    gi = 0
    for w in range(18):
        sunday = first_sunday + datetime.timedelta(days=7*w)
        thursday = sunday - datetime.timedelta(days=3)
        saturday = sunday - datetime.timedelta(days=1)
        monday = sunday + datetime.timedelta(days=1)
        if w == 0:
            kickoff_game_date = kickoff  # season kickoff night (Wed for 2026)
        n_games = 14 if 5 <= w <= 12 else 16
        # pair teams within the week: fewest-games-first balanced draw
        pool = teams.copy()
        placed = []
        used_local = set()
        rng.shuffle(pool)
        guard = 0
        while len(placed) < n_games and guard < 6000:
            guard += 1
            # candidate teams: least-used first for balance
            cand = [t for t in teams if t not in used_local]
            if len(cand) < 2: break
            cand.sort(key=lambda t: (counts[t], rng.random()))
            a = cand[0]
            # pick b among legal partners, prefer least used
            partners = []
            for b in cand[1:]:
                if len(partners) >= 8: break
                key = tuple(sorted((a,b)))
                if pair_cap[key] > 0:
                    partners.append(b)
            if not partners:
                used_local.add(a); continue
            b = min(partners, key=lambda t: counts[t])
            key = tuple(sorted((a,b)))
            pair_cap[key] -= 1
            placed.append((a,b)); used_local.add(a); used_local.add(b)
            counts[a] += 1; counts[b] += 1
        # assign slots
        if w == 0:
            slot_plan = [(kickoff_game_date.isoformat(), "17:20", "KICKOFF")] + \
                        [(thursday.isoformat(), "17:15", "THU")] + \
                        [(sunday.isoformat(), s, t) for s, t in
                         [("10:00","SUN-EARLY"),("10:05","SUN-EARLY"),("10:25","SUN-EARLY"),("10:00","SUN-EARLY"),("10:25","SUN-EARLY"),
                          ("10:05","SUN-EARLY"),("10:25","SUN-EARLY"),("10:00","SUN-EARLY"),("10:05","SUN-EARLY"),("10:05","SUN-EARLY"),
                          ("10:25","SUN-EARLY"),("13:05","SUN-LATE"),("13:25","SUN-LATE"),("17:20","SNF")]] + \
                        [(monday.isoformat(), "17:15", "MNF")]
        else:
            sun_slots = [("10:00","SUN-EARLY"),("10:05","SUN-EARLY"),("10:25","SUN-EARLY")] * 4 + [("13:05","SUN-LATE"),("13:25","SUN-LATE")]
            rng.shuffle(sun_slots)
            n_sun = n_games - 3  # 1 TNF + 1 SNF + 1 MNF
            sun_plan = sun_slots[:n_sun]
            slot_plan = [(thursday.isoformat(), "17:15", "TNF")] + \
                        [(sunday.isoformat(), s, t) for s, t in sun_plan] + \
                        [(sunday.isoformat(), "17:20", "SNF"), (monday.isoformat(), "17:15", "MNF")]
        for k, (pair, (date, slot, tag)) in enumerate(zip(placed, slot_plan)):
            gi += 1
            a, b = pair
            sf_involved = (a == "SF" or b == "SF")
            games.append(row(f"NFL-{year}-{gi:04d}", "NFL", "NFL", "regular", date, slot,
                             DUR["NFL"], name[a], name[b],
                             "high" if sf_involved else "normal", False,
                             "https://www.nfl.com/schedules/",
                             "NFL.com schedule (ESTIMATED reconstruction — see Flagged for Review)",
                             note=f"Week {w+1} ({tag}). Estimated matchup/time; 272-game model with byes ignored at game level.",
                             flags=["estimated", tag.lower()]))
    if year == 2026:
        games = [g for g in games if not (g["away"].startswith("San Francisco") or g["home"].startswith("San Francisco"))]
        niners = [
            ("2026-09-10","17:35","San Francisco 49ers","Los Angeles Rams (Melbourne Cricket Ground, AUS)","Netflix · TNF international · Week 1",True),
            ("2026-09-20","13:25","Miami Dolphins","San Francisco 49ers","FOX · Week 2",True),
            ("2026-09-27","13:05","Arizona Cardinals","San Francisco 49ers","FOX · Week 3",True),
            ("2026-10-04","13:25","Denver Broncos","San Francisco 49ers","CBS · Week 4",True),
            ("2026-10-11","13:25","San Francisco 49ers","Seattle Seahawks (Lumen Field)","FOX · Week 5",True),
            ("2026-10-19","17:15","Washington Commanders","San Francisco 49ers","ESPN & ABC · MNF · Week 6",True),
            ("2026-10-25","10:00","San Francisco 49ers","Atlanta Falcons","FOX · Week 7",True),
            ("2026-11-08","13:05","Las Vegas Raiders","San Francisco 49ers","CBS · Week 9",True),
            ("2026-11-15","13:25","San Francisco 49ers","Dallas Cowboys","FOX · Week 10",True),
            ("2026-11-22","17:20","Minnesota Vikings","San Francisco 49ers (Estadio Banorte, Mexico City)","NBC · SNF · Week 11",True),
            ("2026-11-29","13:25","Seattle Seahawks","San Francisco 49ers","FOX · Week 12",True),
            ("2026-12-06","10:00","San Francisco 49ers","New York Giants","FOX · Week 13",True),
            ("2026-12-13","13:25","Los Angeles Rams","San Francisco 49ers","FOX · Week 14",True),
            ("2026-12-17","17:15","San Francisco 49ers","Los Angeles Chargers","Prime Video · TNF · Week 15",True),
            ("2026-12-27","13:25","San Francisco 49ers","Kansas City Chiefs","CBS · Week 16",True),
            ("2027-01-03","17:20","Philadelphia Eagles","San Francisco 49ers","NBC · SNF · Week 17",True),
            ("2027-01-10","TBD","San Francisco 49ers","Arizona Cardinals","Week 18 — Sat Jan 9 or Sun Jan 10; time TBA under NFL flex rules",False),
        ]
        for i,(date,slot,away,home,note,ok) in enumerate(niners):
            games.append(row(f"SF-2026-{i+1:02d}", "NFL", "NFL", "regular", date, None if slot=="TBD" else slot,
                             DUR["NFL"], away, home, "high", ok,
                             "https://49ers.1rmg.com/news-releases/49ers-announce-2026-schedule/",
                             "49ers official schedule release (May 2026)",
                             note=note, flags=([] if ok else ["tbd","flex_scheduling"])))
        preseason = [("2026-08-13","Tennessee Titans (home)","KPIX 5 · preseason Week 1 (time secondary-source)"),
                     ("2026-08-20","at Los Angeles Chargers","7:00 PM PT · KPIX 5 · preseason Week 2 (time secondary-source)"),
                     ("2026-08-27","at Las Vegas Raiders","KPIX 5 · preseason Week 3 (time secondary-source)")]
        for i,(date,opp,note) in enumerate(preseason):
            games.append(row(f"SF-PRE-2026-{i+1}", "NFL", "NFL", "preseason", date, None,
                             DUR["NFL"], "San Francisco 49ers", opp, "high", False,
                             "https://49ers.1rmg.com/news-releases/49ers-announce-2026-schedule/",
                             "49ers official release (times not printed — flagged)",
                             note=note, flags=["preseason","time_unverified"]))
    return games


def gen_nfl_preseason(year, start_date, weeks=3, rng=None):
    rng = rng or random.Random(0)
    games = []; gi = 0
    for wk in range(weeks):
        gw = d_add(start_date, 7*wk)
        # one Thursday game + 15 Saturday/Sunday games per week (approx), mostly Thu/Sat/Sun
        dates = [d_add(gw, days) for days in (3,5,6,6,6,5,6,6,3,5,6,6,3,6,6,6)]
        pool = NFL_TEAMS.copy(); rng.shuffle(pool)
        pairs = [(pool[i], pool[i+1]) for i in range(0, 30, 2)]
        for k,(pair,date) in enumerate(zip(pairs, dates)):
            gi += 1
            A, B = pair
            sf_involved = (A[0]=="SF" or B[0]=="SF")
            slot = "17:00" if k % 5 == 0 else rng.choice(["16:00","13:00","19:00"])
            games.append(row(f"PRE-{year}-{gi:03d}", "NFL", "NFL", "preseason", date, slot,
                             DUR["NFL"], A[1], B[1], "high" if sf_involved else "normal", False,
                             "https://www.nfl.com/schedules/",
                             "NFL preseason (ESTIMATED — dates not released)",
                             note=f"Preseason week {wk+1}. Estimated; Hall of Fame/league conflicts ignored.",
                             flags=["estimated","preseason"]))
    return games

def gen_nfl_postseason(year, dates_verify, rng, label_note):
    """dates_verify: list of (date, n_games, label, verified, time)"""
    games = []; gi = 0
    for date, n, label, verified, slot in dates_verify:
        for k in range(n):
            gi += 1
            home, away = rng.choice(NFL_TEAMS), rng.choice(NFL_TEAMS)
            while away[0] == home[0]: away = rng.choice(NFL_TEAMS)
            games.append(row(f"POST-NFL-{year}-{gi:03d}", "NFL", "NFL", "postseason", date, slot,
                             DUR["NFL"], away[1], home[1], "normal", verified,
                             "https://www.nfl.com/schedules/postseason",
                             f"NFL postseason {year}–{str(year+1)[-2:]} · {label}",
                             note="Matchup TBD.",
                             flags=["postseason"] + ([] if verified else ["estimated"])))
    return games

# ----------------------------------------------------------------------------- NCAAF (Stanford & Cal only, plus bowls/CFP context)
def stanford_cal_2026():
    """2026 Stanford & Cal — official ACC/athletics releases. Results included where played."""
    rows = []
    stanford = [  # (date, opponent, time PT or None, result/note, source)
        ("2026-08-29","Hawai'i (Stanford)","16:00","W 37–27","https://theacc.com/schedule.aspx?schedule=4617"),
        ("2026-09-04","Miami (Stanford)","18:00","L 6–45","https://theacc.com/schedule.aspx?schedule=4617"),
        ("2026-09-19","at Duke","12:00","L 7–35","https://theacc.com/schedule.aspx?schedule=4617"),
        ("2026-09-26","Georgia Tech (Stanford)","19:00","W 34–27","https://theacc.com/schedule.aspx?schedule=4617"),
        ("2026-10-03","at Wake Forest",None,"L 3–57","https://theacc.com/schedule.aspx?schedule=4617"),
        ("2026-10-10","at Notre Dame","09:30","L 7–58","https://theacc.com/schedule.aspx?schedule=4617"),
        ("2026-10-17","Elon (Stanford)","16:30","W 34–7","https://theacc.com/schedule.aspx?schedule=4617"),
        ("2026-10-23","NC State (Stanford)","19:30","W 31–28","https://theacc.com/schedule.aspx?schedule=4617"),
        ("2026-10-31","at Louisville",None,"L 24–52","https://theacc.com/schedule.aspx?schedule=4617"),
        ("2026-11-14","at Virginia Tech",None,"W 40–22","https://theacc.com/schedule.aspx?schedule=4617"),
        ("2026-11-21","at California — 129th Big Game","16:30","W 44–28 · 7:30 PM ET on ACC Network","https://theacc.com/schedule.aspx?schedule=4617"),
        ("2026-11-28","SMU (Stanford)","12:30","Final week; kickoff 3:30 p.m. ET per ACC","https://theacc.com/schedule.aspx?schedule=4617"),
    ]
    cal = [
        ("2026-09-05","UCLA (California)","19:30","L 24–45","https://calbears.com/sports/football/schedule/text"),
        ("2026-09-12","at Syracuse","12:30","W 21–18","https://calbears.com/sports/football/schedule/text"),
        ("2026-09-19","Wagner (California)","12:30","W 49–7","https://calbears.com/sports/football/schedule/text"),
        ("2026-09-25","Clemson (California)","19:30","L 10–24","https://calbears.com/sports/football/schedule/text"),
        ("2026-10-03","at UNLV","12:30","L 31–39","https://calbears.com/sports/football/schedule/text"),
        ("2026-10-10","Virginia Tech (California)","12:30","W 25–20","https://calbears.com/sports/football/schedule/text"),
        ("2026-10-17","Wake Forest (California)",None,"Result TBA in checked sources; ACC page lists Oct 17","https://calbears.com/sports/football/schedule/text"),
        ("2026-10-24","at SMU",None,"Time TBA in checked sources","https://calbears.com/sports/football/schedule/text"),
        ("2026-10-31","at NC State",None,"Time TBA in checked sources","https://calbears.com/sports/football/schedule/text"),
        ("2026-11-14","at Virginia",None,"Time TBA in checked sources","https://calbears.com/sports/football/schedule/text"),
        ("2026-11-21","Stanford (California) — Big Game","16:30","L 28–44 · 7:30 PM ET on ACC Network","https://calbears.com/sports/football/schedule/text"),
        ("2026-11-28","Pittsburgh (California)",None,"Time TBA in checked sources","https://calbears.com/sports/football/schedule/text"),
    ]
    for i,(date,opp,slot,note,src) in enumerate(stanford):
        tbd = slot is None
        away, home = opponent_team("Stanford", opp)
        rows.append(row(f"STAN-2026-{i+1:02d}","NCAAF","NCAAF (ACC)","regular",date,slot,DUR["NCAAF"],
                        away, home, "high", True,
                        src, "ACC official schedule / gostanford.com",
                        note=note, flags=(["time_unverified"] if tbd else [])))
    for i,(date,opp,slot,note,src) in enumerate(cal):
        tbd = slot is None
        away, home = opponent_team("California", opp)
        rows.append(row(f"CAL-2026-{i+1:02d}","NCAAF","NCAAF (ACC)","regular",date,slot,DUR["NCAAF"],
                        away, home, "high", True,
                        src, "ACC official schedule / calbears.com",
                        note=note, flags=(["time_unverified"] if tbd else [])))
    # Bowl / championship context (not Stanford/Cal-guaranteed; informational flags)
    rows.append(row("ACC-CG-2026","NCAAF","NCAAF (ACC)","postseason","2026-12-05","09:00",DUR["NCAAF"],
                    "ACC Championship Game (participants TBD)","Charlotte — Bank of America Stadium","normal",False,
                    "https://theacc.com/","ACC Championship Game 2026 (date secondary-source)",
                    note="Stanford/Cal qualification not confirmed in checked sources; banner date only.",
                    flags=["estimated","conference_championship","participants_tbd"]))
    return rows

def opponent_team(home_team, opp):
    """Turn opponent string into (away, home) names for display."""
    import re
    opp = opp.strip()
    m = re.search(r'^(.*?)\s*\((Stanford|California)\)', opp)
    if m and m.group(2) == home_team:
        return (m.group(1).strip(), home_team)
    if opp.startswith("at "):
        return (home_team, opp[3:].strip())
    return (opp, home_team)

def stanford_cal_future(year, rng):
    """Estimated 12-game ACC slates on typical Saturday slots; season Late Aug - Thanksgiving week."""
    rows = []
    for team, abbr in (("Stanford Cardinal","STAN"), ("California Golden Bears","CAL")):
        # anchor to a Saturday near Aug 28
        d = d_parse(f"{year}-08-25")
        while d.strftime("%a") != "Sat":
            d += datetime.timedelta(days=1)
        gi = 0
        weeks = [0,1,2,4,5,6,7,8,9,11,12,13]  # typical Saturday offsets w/ a bye
        for w in weeks:
            gi += 1
            date = (d + datetime.timedelta(days=7*w)).isoformat()
            rows.append(row(f"{abbr}-{year}-{gi:02d}","NCAAF","NCAAF (ACC)","regular",date,
                            "16:00",DUR["NCAAF"], f"Opponent TBA ({team})", team, "high", False,
                            "https://theacc.com/","ACC (ESTIMATED slate — not released)",
                            note="Estimated Saturday slot; opponents and dates not released.",
                            flags=["estimated","opponent_tba"]))
        # Big Game — fourth Sat of November
        big = d_parse(f"{year}-11-22")
        while big.strftime("%a") != "Sat":
            big += datetime.timedelta(days=1)
        gi += 1
        rival = "California Golden Bears" if team.startswith("Stanford") else "Stanford Cardinal"
        rows.append(row(f"{abbr}-{year}-{gi:02d}","NCAAF","NCAAF (ACC)","regular",big.isoformat(),
                        "19:30",DUR["NCAAF"], rival, team, "high", False,
                        "https://www.stanford.edu/","Big Game (ESTIMATED date — Nov 2026 was Nov 21)",
                        note="Estimated Big Game Saturday; venue alternates; verify with ACC release.",
                        flags=["estimated","big_game"]))
    return rows

# ----------------------------------------------------------------------------- Westwood One national NFL broadcasts (verified snapshot)
def westwood_one_nfl():
    """Captured live from westwoodonesports.com/nfl-schedule/ on 2026-11-25. ET times converted to PT (-3h)."""
    E = "https://www.westwoodonesports.com/events/"
    rows = [
        ("2026-11-25","16:30",548511,"Green Bay Packers at Los Angeles Rams","TNF international · Thanksgiving Wednesday"),
        ("2026-11-26","09:30",548512,"Chicago Bears at Detroit Lions","Thanksgiving tripleheader (12:30 ET)"),
        ("2026-11-26","13:15",548513,"Philadelphia Eagles at Dallas Cowboys","Thanksgiving tripleheader (4:15 ET)"),
        ("2026-11-26","17:00",548514,"Kansas City Chiefs at Buffalo Bills","Thanksgiving tripleheader (8:00 ET)"),
        ("2026-11-27","11:30",548515,"Denver Broncos at Pittsburgh Steelers","Black Friday (2:30 ET)"),
        ("2026-11-29","16:30",548502,"Las Vegas Raiders at Cleveland Browns","Sunday Night Football"),
        ("2026-11-30","16:00",548544,"Carolina Panthers at Tampa Bay Buccaneers","Monday Night Football"),
        ("2026-12-03","16:30",548566,"Kansas City Chiefs at Los Angeles Rams","Thursday Night Football"),
        ("2026-12-06","16:30",548503,"Houston Texans at Pittsburgh Steelers","Sunday Night Football"),
        ("2026-12-07","16:00",548545,"Dallas Cowboys at Seattle Seahawks","Monday Night Football"),
        ("2026-12-10","16:30",548567,"Minnesota Vikings at New England Patriots","Thursday Night Football"),
        ("2026-12-13","16:30",548505,"Buffalo Bills at Green Bay Packers","Sunday Night Football"),
        ("2026-12-14","16:00",548546,"Pittsburgh Steelers at Jacksonville Jaguars","Monday Night Football"),
        ("2026-12-17","16:30",548568,"San Francisco 49ers at Los Angeles Chargers","Thursday Night Football · 49ers"),
        ("2026-12-19","13:30",548517,"Seattle Seahawks at Philadelphia Eagles","Week 15 Saturday doubleheader (4:30 ET)"),
        ("2026-12-19","17:00",548518,"Chicago Bears at Buffalo Bills","Week 15 Saturday doubleheader (8:00 ET)"),
        ("2026-12-20","16:30",548506,"Detroit Lions at Minnesota Vikings","Sunday Night Football"),
        ("2026-12-21","16:00",548548,"New England Patriots at Kansas City Chiefs","Monday Night Football"),
        ("2026-12-24","16:30",548569,"Houston Texans at Philadelphia Eagles","Thursday Night Football · Christmas Eve"),
        ("2026-12-25","09:30",548528,"Green Bay Packers at Chicago Bears","Christmas Day tripleheader (12:30 ET)"),
        ("2026-12-25","13:15",548531,"Buffalo Bills at Denver Broncos","Christmas Day tripleheader (4:15 ET)"),
        ("2026-12-25","17:00",548534,"Los Angeles Rams at Seattle Seahawks","Christmas Day tripleheader (8:00 ET)"),
        ("2026-12-26","13:00",548519,"Week 16 Saturday doubleheader TBA","Week 16 Saturday (4:00 ET)"),
        ("2026-12-26","17:00",548520,"Week 16 Saturday doubleheader TBA","Week 16 Saturday (8:00 ET)"),
        ("2026-12-27","16:30",548507,"Jacksonville Jaguars at Dallas Cowboys","Sunday Night Football"),
        ("2026-12-28","16:00",548550,"New York Giants at Detroit Lions","Monday Night Football"),
        ("2026-12-31","16:30",548570,"Baltimore Ravens at Cincinnati Bengals","Thursday Night Football"),
        ("2027-01-02","13:00",548521,"Week 17 Saturday doubleheader TBA","Week 17 Saturday (4:00 ET)"),
        ("2027-01-02","17:00",548522,"Week 17 Saturday doubleheader TBA","Week 17 Saturday (8:00 ET)"),
        ("2027-01-03","16:30",548509,"Philadelphia Eagles at San Francisco 49ers","Sunday Night Football · 49ers"),
        ("2027-01-04","16:00",548552,"Houston Texans at Green Bay Packers","Monday Night Football"),
        ("2027-01-09","09:30",548523,"Week 18 Saturday tripleheader TBA","Week 18 Saturday (12:30 ET)"),
        ("2027-01-09","13:15",548524,"Week 18 Saturday tripleheader TBA","Week 18 Saturday (4:15 ET)"),
        ("2027-01-09","17:00",548526,"Week 18 Saturday tripleheader TBA","Week 18 Saturday (8:00 ET)"),
        ("2027-01-10","16:30",548510,"Week 18 Sunday Night Football TBA","Week 18 Sunday Night Football"),
    ]
    rows_out = []
    for i,(date,pt,eid,title,note) in enumerate(rows):
        sf = "49ers" in title
        rows_out.append(row(f"WW1-{eid}","WW1","Westwood One Sports · NFL","regular",date,pt,
                            DUR["NFL"], title.split(" at ")[0] if " at " in title else title,
                            title.split(" at ")[1] if " at " in title else "", "high", True,
                            f"{E}{eid}", "westwoodonesports.com (official) — captured 2026-11-25",
                            note=note, flags=["ww1_national"] + (["49ers"] if sf else [])))
    # WW1 national NCAAF broadcasts (informational; NOT in free-time definition)
    ncaaf = [("2026-11-28","08:30","Michigan at Ohio State","Big Ten — 11:30 ET","https://www.westwoodonesports.com/events/557131",557131),
             ("2026-12-05","12:30","SEC Championship Game","Atlanta — 3:30 ET","https://www.westwoodonesports.com/events/557146",557146),
             ("2026-12-12","11:00","Army vs Navy","East Rutherford — 2:00 ET","https://www.westwoodonesports.com/events/557132",557132)]
    for i,(date,pt,title,note,src,eid) in enumerate(ncaaf):
        if " at " in title:
            ww_away, ww_home = title.split(" at ", 1)
        else:
            ww_away, ww_home = title, ""
        rows_out.append(row(f"WW1NCAAF-{eid}","WW1","Westwood One Sports · NCAAF (informational)","regular",date,pt,
                            DUR["NCAAF"], ww_away, ww_home, "normal", True,
                            src, "westwoodonesports.com (official) — captured 2026-11-25",
                            note=f"Informational: NOT counted in the free-time definition (only Stanford/Cal NCAAF counts). {note}",
                            flags=["ww1_ncaaf_informational"]))
    return rows_out

# ----------------------------------------------------------------------------- Verified / anchored extra rows
def mlb_anchors():
    A = []
    A.append(row("MLB-2026-OPENING-NIGHT","MLB","MLB","regular","2026-03-25","17:05",DUR["MLB_regular"],
                 "New York Yankees","San Francisco Giants (Oracle Park)","high",True,
                 "https://www.mlb.com/press-release/press-release-game-times-announced-for-2026-regular-season-spring-training-spring-breakout-games",
                 "MLB.com official press release (Jan 2026) + mlbschedule.net",
                 note="Standalone Opening Night. Giants home opener vs Yankees.",
                 flags=["opening_night"]))
    A.append(row("MLB-2026-OPENING-DAY","MLB","MLB","regular","2026-03-26","10:15",DUR["MLB_regular"],
                 "Pittsburgh Pirates","New York Mets (1:15 ET, NBC/Peacock)","normal",True,
                 "https://www.mlb.com/press-release/press-release-game-times-announced-for-2026-regular-season-spring-training-spring-breakout-games",
                 "MLB.com official press release (Jan 2026)",
                 note="Traditional Opening Day — 11 games; Dodgers host Arizona 5:30 PT on NBC/Peacock.",
                 flags=["opening_day"]))
    A.append(row("MLB-2026-ASTAR","MLB","MLB","all_star","2026-07-14","17:00",DUR["MLB_allstar"],
                 "AL","NL — Citizens Bank Park, Philadelphia","normal",False,
                 "https://www.mlbschedule.net/blog/when-does-mlb-season-end-2026",
                 "mlbschedule.net + press summaries (partial-secondary)",
                 note="97th? 2026 All-Star Game — date verified via multiple secondary sources; official MLB confirmation recommended.",
                 flags=["all_star","partial_secondary"]))
    A.append(row("MLB-2026-FINALE","MLB","MLB","regular","2026-09-27","12:00",DUR["MLB_regular"],
                 "All 30 clubs","15 games, 3:00–3:20 PM ET first pitch","normal",True,
                 "https://www.mlb.com/press-release/press-release-game-times-announced-for-2026-regular-season-spring-training-spring-breakout-games",
                 "MLB.com official press release (Jan 2026)",
                 note="Regular-season finale; all 30 clubs play.",
                 flags=["finale"]))
    A.append(row("MLB-2027-OPENING-NIGHT","MLB","MLB","regular","2027-03-24","17:05",DUR["MLB_regular"],
                 "Matchup TBA","Opening Night (Netflix)","normal",False,
                 "https://en.wikipedia.org/wiki/2027_Major_League_Baseball_season",
                 "Wikipedia 2027 season article + club releases (partial-secondary)",
                 note="2027 MLB schedule released Jul 16, 2026. Opening Night matchup TBA at release.",
                 flags=["opening_night","partial_secondary"]))
    A.append(row("MLB-2027-OPENING-DAY","MLB","MLB","regular","2027-03-25","13:05",DUR["MLB_regular"],
                 "14 games incl. Brewers vs Angels","Opening Day (earliest in MLB history)","normal",True,
                 "https://www.mlb.com/brewers/press-release/brewers-announce-2027-regular-season-schedule",
                 "MLB.com official club press releases (Orioles, Brewers, Rays)",
                 note="2027 Opening Day Mar 25, 2027 — verified via official club releases on MLB.com.",
                 flags=["opening_day"]))
    A.append(row("MLB-2027-ALL-PLAY","MLB","MLB","regular","2027-03-27","13:05",DUR["MLB_regular"],
                 "All 30 clubs","League-wide slate","normal",True,
                 "https://en.wikipedia.org/wiki/2027_Major_League_Baseball_season",
                 "Wikipedia + club releases (partial-secondary)",
                 note="All 30 clubs play Mar 27, 2027.", flags=["opening_weekend","partial_secondary"]))
    A.append(row("MLB-2027-ASTAR","MLB","MLB","all_star","2027-07-13","20:00",DUR["MLB_allstar"],
                 "AL","NL — Wrigley Field, Chicago (97th All-Star Game)","normal",False,
                 "https://en.wikipedia.org/wiki/2027_Major_League_Baseball_season",
                 "Wikipedia (partial-secondary)",
                 note="97th All-Star Game — July 13, 2027, Wrigley Field.", flags=["all_star","partial_secondary"]))
    A.append(row("MLB-2027-RIVALRY","MLB","MLB","regular","2027-07-17","13:05",DUR["MLB_regular"],
                 "Rivalry Weekend","Interleague marquee slate (Jul 15–18)","normal",False,
                 "https://en.wikipedia.org/wiki/2027_Major_League_Baseball_season",
                 "Wikipedia (partial-secondary)",
                 note="Rivalry Weekend Jul 15–18, 2027.", flags=["rivalry_weekend","partial_secondary"]))
    A.append(row("MLB-2027-FOD","MLB","MLB","regular","2027-08-12","18:15",DUR["MLB_regular"],
                 "Boston Red Sox","Kansas City Royals — Field of Dreams, Dyersville","normal",False,
                 "https://en.wikipedia.org/wiki/2027_Major_League_Baseball_season",
                 "Wikipedia (partial-secondary)",
                 note="MLB at Field of Dreams Aug 12, 2027.", flags=["special_event","partial_secondary"]))
    A.append(row("MLB-2027-LLC","MLB","MLB","regular","2027-08-19","17:10",DUR["MLB_regular"],
                 "Chicago Cubs","Toronto Blue Jays — Little League Classic, Williamsport","normal",False,
                 "https://en.wikipedia.org/wiki/2027_Major_League_Baseball_season",
                 "Wikipedia (partial-secondary)",
                 note="MLB Little League Classic Aug 19, 2027.", flags=["special_event","partial_secondary"]))
    A.append(row("MLB-2027-FINALE","MLB","MLB","regular","2027-09-26","13:05",DUR["MLB_regular"],
                 "All 30 clubs","Final series Sep 24–26, 2027","normal",True,
                 "https://www.mlb.com/orioles/press-release/orioles-announce-2027-regular-season-schedule",
                 "MLB.com official club press releases",
                 note="2027 regular season ends Sep 26, 2027.", flags=["finale"]))
    A.append(row("MLB-2028-OPEN-NIGHT","MLB","MLB","regular","2028-03-29","17:05",DUR["MLB_regular"],
                 "Matchup TBD","Estimated Opening Night","normal",False,
                 "https://www.mlb.com/schedule","ESTIMATED — 2028 schedule not released",
                 note="No 2028 schedule released as of 2026-11-25.", flags=["estimated"]))
    A.append(row("MLB-2028-OPEN-DAY","MLB","MLB","regular","2028-03-30","13:05",DUR["MLB_regular"],
                 "Opening Day (estimated)","Estimated Opening Day","normal",False,
                 "https://www.mlb.com/schedule","ESTIMATED — 2028 schedule not released",
                 note="2028 schedule expected ~mid-2027.", flags=["estimated"]))
    A.append(row("MLB-2028-ASTAR","MLB","MLB","all_star","2028-07-11","17:00",DUR["MLB_allstar"],
                 "AL","NL — All-Star Game (estimated date)","normal",False,
                 "https://www.mlb.com/all-star","ESTIMATED",
                 note="Estimated; no 2028 All-Star details released.", flags=["estimated","all_star"]))
    A.append(row("MLB-2029-OPEN-NIGHT","MLB","MLB","regular","2029-03-28","17:05",DUR["MLB_regular"],
                 "Matchup TBD","Estimated Opening Night","normal",False,
                 "https://www.mlb.com/schedule","ESTIMATED — 2029 schedule not released",
                 note="No 2029 schedule released as of 2026-11-25.", flags=["estimated"]))
    A.append(row("MLB-2029-OPEN-DAY","MLB","MLB","regular","2029-03-29","13:05",DUR["MLB_regular"],
                 "Opening Day (estimated)","Estimated Opening Day","normal",False,
                 "https://www.mlb.com/schedule","ESTIMATED — 2029 schedule not released",
                 note="2029 schedule expected ~mid-2028.", flags=["estimated"]))
    A.append(row("MLB-2029-ASTAR","MLB","MLB","all_star","2029-07-10","17:00",DUR["MLB_allstar"],
                 "AL","NL — All-Star Game (estimated date)","normal",False,
                 "https://www.mlb.com/all-star","ESTIMATED",
                 note="Estimated; no 2029 All-Star details released.", flags=["estimated","all_star"]))
    return A

def nfl_anchors():
    A = []
    A.append(row("NFL-2026-KICKOFF","NFL","NFL","regular","2026-09-09","17:20",DUR["NFL"],
                 "New England Patriots","Seattle Seahawks (Lumen Field)","normal",False,
                 "https://www.usatoday.com/story/sports/nfl/2026/05/14/full-nfl-schedule-release-2026-all-games/90067398007/",
                 "USA Today summary of NFL May 14, 2026 release (partial-secondary)",
                 note="2026 NFL kickoff. Super Bowl LX rematch.", flags=["kickoff","partial_secondary"]))
    A.append(row("NFL-2026-SB","NFL","NFL","postseason","2027-02-14","15:30",230,
                 "AFC champion","NFC champion — Super Bowl LXI, SoFi Stadium (Inglewood, CA)","normal",False,
                 "https://en.wikipedia.org/wiki/List_of_Super_Bowl_champions",
                 "Wikipedia upcoming-games table + secondary (date conflict Feb 14 vs 15 flagged)",
                 note="Super Bowl LXI — Feb 14, 2027 (flagged for review). ABC/ESPN; ~3:30 PT kickoff per convention.",
                 flags=["super_bowl","flagged_review"]))
    A.append(row("NFL-2026-SB60","NFL","NFL","postseason","2026-02-08","15:30",230,
                 "AFC champion","NFC champion — Super Bowl LX, Levi's Stadium (Santa Clara, CA)","normal",False,
                 "https://en.wikipedia.org/wiki/List_of_Super_Bowl_champions",
                 "Wikipedia (occurred 2026-02-08; Seahawks won 29–13 per reports)",
                 note="Super Bowl LX — Feb 8, 2026 at Levi's Stadium.", flags=["super_bowl","played"]))
    A.append(row("NFL-2028-SB","NFL","NFL","postseason","2028-02-13","15:30",230,
                 "AFC champion","NFC champion — Super Bowl LXII, Mercedes-Benz Stadium (Atlanta, GA)","normal",False,
                 "https://en.wikipedia.org/wiki/List_of_Super_Bowl_champions",
                 "Wikipedia + host-city announcement (exact date TBA pending 18-game expansion)",
                 note="Super Bowl LXII — February 2028 (Feb 13 per convention; flagged).",
                 flags=["super_bowl","flagged_review"]))
    A.append(row("NFL-2029-SB","NFL","NFL","postseason","2029-02-11","15:30",230,
                 "AFC champion","NFC champion — Super Bowl LXIII, Allegiant Stadium (Las Vegas, NV)","normal",False,
                 "https://en.wikipedia.org/wiki/List_of_Super_Bowl_champions",
                 "Wikipedia + host-city announcement (date TBA)",
                 note="Super Bowl LXIII — February 2029 (Feb 11 per convention; flagged).",
                 flags=["super_bowl","flagged_review"]))
    # Pro Bowl Games (estimated dates — verify)
    A.append(row("PROBOWL-2027","NFL","NFL","all_star","2027-02-07","14:00",165,
                 "AFC","NFC — Pro Bowl Games (estimated)","normal",False,
                 "https://www.nfl.com/news/","ESTIMATED — Pro Bowl date not verified in checked sources",
                 note="Pro Bowl Games weekend before Super Bowl LXI; date not confirmed — flagged.",
                 flags=["all_star","estimated","flagged_review"]))
    A.append(row("PROBOWL-2028","NFL","NFL","all_star","2028-02-06","14:00",165,
                 "AFC","NFC — Pro Bowl Games (estimated)","normal",False,
                 "https://www.nfl.com/news/","ESTIMATED — Pro Bowl date not verified in checked sources",
                 note="Pro Bowl Games weekend before Super Bowl LXII; date not confirmed — flagged.",
                 flags=["all_star","estimated","flagged_review"]))
    A.append(row("PROBOWL-2029","NFL","NFL","all_star","2029-02-04","14:00",165,
                 "AFC","NFC — Pro Bowl Games (estimated)","normal",False,
                 "https://www.nfl.com/news/","ESTIMATED — Pro Bowl date not verified in checked sources",
                 note="Pro Bowl Games weekend before Super Bowl LXIII; date not confirmed — flagged.",
                 flags=["all_star","estimated","flagged_review"]))
    # CFP championship context rows (informational — only counts if Stanford/Cal participates)
    A.append(row("CFP-2027","NCAAF","NCAAF (CFP, informational)","postseason","2027-01-25","17:00",230,
                 "TBD","TBD — CFP National Championship, Allegiant Stadium (Las Vegas)","normal",True,
                 "https://collegefootballplayoff.com/","collegefootballplayoff.com (official) — announced date",
                 note="Informational only. Counts in busy calculus ONLY if Stanford or Cal participates.",
                 flags=["cfp","informational","stanford_cal_participation_tbd"]))
    A.append(row("CFP-2028","NCAAF","NCAAF (CFP, informational)","postseason","2028-01-24","17:00",230,
                 "TBD","TBD — CFP National Championship, Caesars Superdome (New Orleans)","normal",True,
                 "https://collegefootballplayoff.com/","collegefootballplayoff.com (official) — announced date",
                 note="Informational only.", flags=["cfp","informational"]))
    A.append(row("CFP-2029","NCAAF","NCAAF (CFP, informational)","postseason","2029-01-22","17:00",230,
                 "TBD","TBD — CFP National Championship, Raymond James Stadium (Tampa)","normal",True,
                 "https://collegefootballplayoff.com/","collegefootballplayoff.com (official) — announced date",
                 note="Informational only.", flags=["cfp","informational"]))
    return A

# ----------------------------------------------------------------------------- Bowling defensive placeholders
def bowl_placeholders(year):
    """If Stanford/Cal are bowl-eligible these dates block; defensive placeholders, eligibility TBD."""
    rows = []
    for team, abbr in (("Stanford Cardinal","STAN"), ("California Golden Bears","CAL")):
        for md, label in ((f"{year}-12-19","Bowl Game (eligibility TBD) — mid-December bowl window"),
                          (f"{year+1}-01-02","Bowl Game (eligibility TBD) — early-January bowl window")):
            rows.append(row(f"{abbr}-BOWL-{md}","NCAAF","NCAAF (bowl, defensive)","bowl",md,"12:00",DUR["NCAAF"],
                            f"Opponent TBA ({team})", team, "high", False,
                            "https://www.espn.com/college-football/bowls",
                            "Bowl window placeholder (defensive — not an announcement)",
                            note="Eligibility unconfirmed. Treat as busy defensively; remove once bowls are announced.",
                            flags=["estimated","bowl","eligibility_tbd"]))
    return rows

# ----------------------------------------------------------------------------- Assembly + analysis
def season_rows(year):
    rng = random.Random(20261125 + year)
    games = []
    WW1 = westwood_one_nfl()
    anchors = mlb_anchors() + nfl_anchors()
    if year == 2026:
        games += gen_mlb_games(2026, "2026-03-26", "2026-09-27", rng)
        games += gen_spring_training(2026, "2026-02-20", "2026-03-24", rng)
        games += gen_mlb_postseason(2026, [("2026-09-29",4,"Wild Card",False),("2026-09-30",4,"Wild Card",False),("2026-10-01",4,"Wild Card",False),
                                           ("2026-10-03",2,"Division Series",False),("2026-10-05",2,"Division Series",False),("2026-10-06",2,"Division Series",False),
                                           ("2026-10-08",2,"Division Series",False),("2026-10-09",2,"Division Series",False),("2026-10-10",2,"Division Series",False),
                                           ("2026-10-13",1,"Championship Series",False),("2026-10-15",1,"Championship Series",False),("2026-10-17",1,"Championship Series",False),("2026-10-19",1,"Championship Series",False),
                                           ("2026-10-23",1,"World Series G1",False),("2026-10-24",1,"World Series G2",False),("2026-10-26",1,"World Series G3",False),
                                           ("2026-10-27",1,"World Series G4",False),("2026-10-28",1,"World Series G5",False),("2026-10-30",1,"World Series G6",False),("2026-10-31",1,"World Series G7",False)], rng)
        games += gen_nfl(2026, "2026-09-09", rng)
        pre = [g for g in gen_nfl_preseason(2026, "2026-08-13", 3, rng) if "San Francisco" not in g["away"] and "San Francisco" not in g["home"]]
        games += pre
        games += gen_nfl_postseason(2026, [("2027-01-16",3,"Wild Card",False,"10:05"),("2027-01-17",2,"Wild Card",False,"10:05"),("2027-01-18",1,"Wild Card (Mon)",False,"17:15"),
                                           ("2027-01-23",2,"Divisional",False,"13:00"),("2027-01-24",2,"Divisional",False,"13:00"),
                                           ("2027-01-31",2,"Conference Championships",False,"12:30")], rng, "")
        games += stanford_cal_2026()
        games += bowl_placeholders(2026) + bowl_placeholders(2025)
        games += gen_nfl_postseason(2025, [("2026-01-10",3,"Wild Card (2025 season)",False,"13:05"),("2026-01-11",2,"Wild Card (2025 season)",False,"13:05"),("2026-01-12",1,"Wild Card Mon (2025 season)",False,"17:15"),
                                           ("2026-01-17",2,"Divisional (2025 season)",False,"16:30"),("2026-01-18",2,"Divisional (2025 season)",False,"12:00"),
                                           ("2026-01-25",2,"Conference Championships (2025 season)",False,"12:30")], rng, "")
        games.append(row("CFP-2026","NCAAF","NCAAF (CFP, informational)","postseason","2026-01-19","17:00",230,
                         "TBD","TBD — CFP National Championship, Hard Rock Stadium (Miami Gardens)","normal",True,
                         "https://collegefootballplayoff.com/","collegefootballplayoff.com (announced) — Jan 19, 2026",
                         note="Informational only.", flags=["cfp","informational"]))
        games.append(row("PROBOWL-2026","NFL","NFL","all_star","2026-02-01","14:00",165,
                         "AFC","NFC — Pro Bowl Games (estimated date)","normal",False,
                         "https://www.nfl.com/news/","ESTIMATED — Pro Bowl date not verified in checked sources",
                         note="Estimated; flagged for review.", flags=["all_star","estimated","flagged_review"]))
        games += [r for r in WW1 if r['date'].startswith(str(year))]
    elif year == 2027:
        games += gen_mlb_games(2027, "2027-03-25", "2027-09-26", rng)
        games += gen_spring_training(2027, "2027-02-19", "2027-03-23", rng)
        games += gen_mlb_postseason(2027, [("2027-09-28",4,"Wild Card",False),("2027-09-29",4,"Wild Card",False),("2027-09-30",4,"Wild Card",False),
                                           ("2027-10-02",2,"Division Series",False),("2027-10-04",2,"Division Series",False),("2027-10-05",2,"Division Series",False),
                                           ("2027-10-07",2,"Division Series",False),("2027-10-09",2,"Division Series",False),("2027-10-11",2,"Division Series",False),
                                           ("2027-10-13",1,"Championship Series",False),("2027-10-15",1,"Championship Series",False),("2027-10-17",1,"Championship Series",False),("2027-10-19",1,"Championship Series",False),
                                           ("2027-10-22",1,"World Series G1",False),("2027-10-23",1,"World Series G2",False),("2027-10-25",1,"World Series G3",False),
                                           ("2027-10-26",1,"World Series G4",False),("2027-10-27",1,"World Series G5",False),("2027-10-29",1,"World Series G6",False),("2027-10-30",1,"World Series G7",False)], rng)
        games += gen_nfl(2027, "2027-09-09", rng)
        games += gen_nfl_preseason(2027, "2027-08-12", 3, rng)
        games += gen_nfl_postseason(2027, [("2028-01-15",3,"Wild Card",False,"10:05"),("2028-01-16",2,"Wild Card",False,"10:05"),("2028-01-17",1,"Wild Card (Mon)",False,"17:15"),
                                           ("2028-01-22",2,"Divisional",False,"13:00"),("2028-01-23",2,"Divisional",False,"13:00"),
                                           ("2028-01-30",2,"Conference Championships",False,"12:30")], rng, "")
        games += stanford_cal_future(2027, rng) + bowl_placeholders(2027)
        games += [r for r in WW1 if r['date'].startswith(str(year))]
    elif year == 2028:
        games += gen_mlb_games(2028, "2028-03-30", "2028-09-24", rng)
        games += gen_spring_training(2028, "2028-02-18", "2028-03-28", rng)
        games += gen_mlb_postseason(2028, [("2028-09-26",4,"Wild Card",False),("2028-09-27",4,"Wild Card",False),("2028-09-28",4,"Wild Card",False),
                                           ("2028-10-02",2,"Division Series",False),("2028-10-04",2,"Division Series",False),("2028-10-06",2,"Division Series",False),
                                           ("2028-10-08",2,"Division Series",False),("2028-10-10",2,"Division Series",False),
                                           ("2028-10-12",1,"Championship Series",False),("2028-10-14",1,"Championship Series",False),("2028-10-16",1,"Championship Series",False),("2028-10-18",1,"Championship Series",False),
                                           ("2028-10-20",1,"World Series G1",False),("2028-10-21",1,"World Series G2",False),("2028-10-23",1,"World Series G3",False),
                                           ("2028-10-24",1,"World Series G4",False),("2028-10-25",1,"World Series G5",False),("2028-10-27",1,"World Series G6",False),("2028-10-28",1,"World Series G7",False)], rng)
        games += gen_nfl(2028, "2028-09-07", rng)
        games += gen_nfl_preseason(2028, "2028-08-10", 3, rng)
        games += gen_nfl_postseason(2028, [("2029-01-13",3,"Wild Card",False,"10:05"),("2029-01-14",2,"Wild Card",False,"10:05"),("2029-01-15",1,"Wild Card (Mon)",False,"17:15"),
                                           ("2029-01-20",2,"Divisional",False,"13:00"),("2029-01-21",2,"Divisional",False,"13:00"),
                                           ("2029-01-28",2,"Conference Championships",False,"12:30")], rng, "")
        games += stanford_cal_future(2028, rng) + bowl_placeholders(2028)
    elif year == 2029:
        games += gen_mlb_games(2029, "2029-03-29", "2029-09-30", rng)
        games += gen_spring_training(2029, "2029-02-18", "2029-03-27", rng)
        games += gen_mlb_postseason(2029, [("2029-10-02",4,"Wild Card",False),("2029-10-03",4,"Wild Card",False),("2029-10-04",4,"Wild Card",False),
                                           ("2029-10-06",2,"Division Series",False),("2029-10-08",2,"Division Series",False),("2029-10-10",2,"Division Series",False),
                                           ("2029-10-12",2,"Division Series",False),("2029-10-13",2,"Division Series",False),
                                           ("2029-10-15",1,"Championship Series",False),("2029-10-17",1,"Championship Series",False),("2029-10-19",1,"Championship Series",False),("2029-10-20",1,"Championship Series",False),
                                           ("2029-10-26",1,"World Series G1",False),("2029-10-27",1,"World Series G2",False),("2029-10-29",1,"World Series G3",False),
                                           ("2029-10-30",1,"World Series G4",False),("2029-10-31",1,"World Series G5",False),("2029-11-02",1,"World Series G6",False),("2029-11-03",1,"World Series G7",False)], rng)
        games += gen_nfl(2029, "2029-09-06", rng)
        games += gen_nfl_preseason(2029, "2029-08-09", 3, rng)
        games += gen_nfl_postseason(2029, [("2030-01-11",3,"Wild Card",False,"10:05"),("2030-01-12",2,"Wild Card",False,"10:05"),("2030-01-13",1,"Wild Card (Mon)",False,"17:15"),
                                           ("2030-01-18",2,"Divisional",False,"13:00"),("2030-01-19",2,"Divisional",False,"13:00"),
                                           ("2030-01-26",2,"Conference Championships",False,"12:30")], rng, "")
        games += stanford_cal_future(2029, rng) + bowl_placeholders(2029)
    # anchors whose date falls in this year
    for a in anchors:
        if a["date"].startswith(str(year)):
            games.append(a)
    # de-duplicate exact duplicate ids (anchor vs generated) — keep first occurrence, prefer verified
    seen = {}
    for g in games:
        key = (g["date"], g["title"], g["season_type"], g["start"])
        prev = seen.get(key)
        if prev is None or (g["verified"] and not prev["verified"]):
            seen[key] = g
    games = list(seen.values())
    games.sort(key=lambda g: (g["date"], g["start"] or "99:99", g["id"]))
    return games

def to_min(t):
    if not t: return None
    h, m = t.split(":"); return int(h)*60 + int(m)
def clock_pt(mins):
    mins = mins % 1440
    h, m = divmod(mins, 60)
    ampm = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d} {ampm}"

def analyze(year, rows):
    days = d_range(f"{year}-01-01", f"{year}-12-31")
    day = {d: {"timed": [], "untimed": 0, "priority_timed": [], "priority_untimed": 0} for d in days}
    def in_scope(r):
        lg = r["league"]
        if "(informational)" in lg: return False
        return r["season_type"] in ("spring_training","preseason","regular","postseason","all_star","bowl")
    for r in rows:
        if not r["date"].startswith(str(year)): continue
        if not in_scope(r): continue
        dd = day[r["date"]]
        s = to_min(r["start"])
        if s is None:
            dd["untimed"] += 1
            if r["priority"] == "high": dd["priority_untimed"] += 1
            continue
        dd["timed"].append((s, s + r["minutes"], r))
        if r["priority"] == "high":
            dd["priority_timed"].append((s, s + r["minutes"], r))
    out_days = []
    free_strict_days = []
    free_prac_days = []
    for d in days:
        dd = day[d]
        busy = dd["timed"]
        prac = dd["priority_timed"]
        intervals = merge(busy)
        p_intervals = merge(prac)
        free_minutes = 1440 - sum(b - a for a, b in intervals)
        p_free_minutes = 1440 - sum(b - a for a, b in p_intervals)
        has_untimed = dd["untimed"] > 0
        has_p_untimed = dd["priority_untimed"] > 0
        strict_busy_day = bool(intervals) or has_untimed
        prac_busy_day = bool(p_intervals) or has_p_untimed
        if not strict_busy_day: free_strict_days.append(d)
        if not prac_busy_day: free_prac_days.append(d)
        out_days.append({"date": d, "weekday": dow(d),
                         "strict_busy_minutes": 1440 - free_minutes if (intervals or has_untimed) else 0,
                         "strict_free_minutes": free_minutes if not has_untimed else None,
                         "strict_free_day": not strict_busy_day,
                         "strict_untimed_games": dd["untimed"],
                         "practical_busy_minutes": 1440 - p_free_minutes if (p_intervals or has_p_untimed) else 0,
                         "practical_free_minutes": p_free_minutes if not has_p_untimed else None,
                         "practical_free_day": not prac_busy_day,
                         "practical_untimed_games": dd["priority_untimed"]})
    # windows: consecutive free days >= 3
    windows = []
    cur = []
    for rec in out_days:
        key = rec["strict_free_day"]
        if key: cur.append(rec["date"])
        else:
            if len(cur) >= 3: windows.append({"mode":"strict","start":cur[0],"end":cur[-1],"days":len(cur)})
            cur = []
    if len(cur) >= 3: windows.append({"mode":"strict","start":cur[0],"end":cur[-1],"days":len(cur)})
    cur = []
    for rec in out_days:
        key = rec["practical_free_day"]
        if key: cur.append(rec["date"])
        else:
            if len(cur) >= 3: windows.append({"mode":"practical","start":cur[0],"end":cur[-1],"days":len(cur)})
            cur = []
    if len(cur) >= 3: windows.append({"mode":"practical","start":cur[0],"end":cur[-1],"days":len(cur)})
    windows.sort(key=lambda w: -w["days"])
    months = defaultdict(lambda: [0,0])
    for rec in out_days:
        m = rec["date"][:7]
        months[m][0] += 1 if rec["strict_free_day"] else 0
        months[m][1] += 1 if rec["practical_free_day"] else 0
    month_summary = [{"month": m, "free_days_strict": v[0], "free_days_practical": v[1]} for m, v in sorted(months.items())]
    counts = defaultdict(int); pc = defaultdict(int)
    for r in rows:
        if r["date"].startswith(str(year)) and in_scope(r):
            counts[r["sport"]] += 1
            if r["priority"] == "high": pc[r["sport"]] += 1
    return {"year": year, "total_game_rows_in_year": sum(counts.values()),
            "games_by_sport": dict(counts), "high_priority_by_sport": dict(pc),
            "free_days_strict": len(free_strict_days), "free_days_practical": len(free_prac_days),
            "windows": windows, "month_summary": month_summary, "days": out_days}

def merge(intervals):
    out = []
    for s, e, _ in sorted(intervals, key=lambda x: x[0]):
        if e > 1440: e = 1440
        if out and s <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], e))
        else:
            out.append((s, e))
    return out

def main():
    season_pools = {}
    for year in (2026, 2027, 2028, 2029):
        rows = season_rows(year)
        rows = overlay(year, rows)
        season_pools[year] = rows
        print(year, "rows after overlay:", len(rows))
    merged = [g for y in (2026, 2027, 2028, 2029) for g in season_pools[y]]
    merged = global_dedup(merged)
    merged.sort(key=lambda g: (g["date"], g["start"] or "99:99", g["id"]))
    all_rows = {y: [r for r in merged if r["date"].startswith(str(y))] for y in (2026, 2027, 2028, 2029)}
    for year, rows in all_rows.items():
        with open(DATA / f"games-{year}.json", "w") as f:
            json.dump(rows, f, separators=(",", ":"))
        print(year, "games:", len(rows))
    global_pool = merged
    analysis = {}
    for year in (2026, 2027, 2028, 2029):
        analysis[str(year)] = analyze(year, global_pool)
    with open(DATA / "vacation_analysis.json", "w") as f:
        json.dump(analysis, f, separators=(",", ":"))
    meta = {
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "timezone": TZ, "generator": "tools/generate_schedules.py",
        "games_2026": len(all_rows[2026]), "games_2027": len(all_rows[2027]),
        "games_2028": len(all_rows[2028]), "games_2029": len(all_rows[2029]),
        "durations_min": DUR,
        "definition_strict": "A day is busy if any MLB (incl. Spring Training/postseason), NFL (incl. preseason/postseason/Pro Bowl/Super Bowl), or high-scope NCAAF row (Stanford/Cal regular/bowl/conference championship) airs that day. Other NCAAF and informational rows (CFP/WW1-NCAAF) are excluded.",
        "definition_practical": "Busy = priority=high rows only (Giants/Athletics MLB, 49ers NFL, Stanford/Cal NCAAF, Westwood One national NFL). Day-level: any untimed high-priority game makes the day busy.",
        "verification_policy": "verified=true only for rows anchored to an official source: data/all_events.json (VERIFIED rows), data/mlb_2027_bayarea.json (MLB Stats API extract), data/ncaaf_stanford_cal.json, data/westwood_one_2026.json (2026-11-25 capture). All other rows are ESTIMATES anchored to verified season boundaries.",
        "overlays": ["data/all_events.json", "data/mlb_2027_bayarea.json", "data/ncaaf_stanford_cal.json", "data/westwood_one_2026.json"]
    }
    with open(DATA / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    print("meta + vacation_analysis written")


# ----------------------------------------------------------------------------- Official overlay ingestion
import re as _re
import json as _json

def norm_team(name):
    s = _re.sub(r'[^a-z0-9]', '', str(name).lower())
    if s.startswith('athletics'):
        return 'athletics'
    if s == 'sanfranciscogiants':
        return s
    return s

def nkey(date, away, home):
    a, b = norm_team(away), norm_team(home)
    return (date, tuple(sorted((a, b))))

def mins_to_hhmm(mins):
    if mins is None: return None
    h, m = divmod(int(mins), 60)
    return f"{h:02d}:{m:02d}"

def parse_pst(t):
    """'5:00 PM PST' -> minutes since midnight PT; '' -> None"""
    if not t: return None
    m = _re.match(r'(\d+):(\d+)\s*(AM|PM)', str(t).strip(), _re.I)
    if not m: return None
    h, mi, ap = int(m.group(1)), int(m.group(2)), m.group(3).upper()
    if ap == 'PM' and h != 12: h += 12
    if ap == 'AM' and h == 12: h = 0
    return h*60 + mi

def overlay_all_events_verified(year, rows):
    """Pull VERIFIED rows from data/all_events.json (NFL 2026 W12-18 + SB LXI; MLB 2027 verified)."""
    added = 0
    path = ROOT / 'data' / 'all_events.json'
    if not path.exists():
        return rows, 0
    events = _json.load(open(path)).get('events', [])
    out = list(rows)
    for e in events:
        if e.get('status') != 'VERIFIED':
            continue
        if str(e.get('year')) != str(year):
            continue
        lg = e.get('league')
        if lg not in ('MLB', 'NFL', 'NCAAF'):
            continue
        sport = 'MLB' if lg == 'MLB' else ('NFL' if lg == 'NFL' else 'NCAAF')
        phase = e.get('phase', '')
        if 'Spring Training' in phase: season_type = 'spring_training'; minutes = DUR['MLB_spring']
        elif 'All-Star' in phase: season_type = 'all_star'; minutes = DUR['MLB_allstar']
        elif 'Postseason' in phase or 'Super Bowl' in phase or 'Wild Card' in phase or 'Divisional' in phase or 'Conf Champ' in phase: season_type = 'postseason'; minutes = DUR['NFL']
        elif 'Game (Week' in phase or 'Regular Season' in phase: season_type = 'regular'; minutes = DUR['MLB_regular'] if lg == 'MLB' else (DUR['NFL'] if lg == 'NFL' else DUR['NCAAF'])
        else: season_type = 'regular'; minutes = DUR.get('NFL', 183)
        if lg == 'NFL': minutes = e.get('durationMin') or DUR['NFL']
        start = None
        if not e.get('startTimeTBD'):
            start = mins_to_hhmm(e.get('startMinPST')) or mins_to_hhmm(parse_pst(e.get('officialTimePST')))
        priority = 'high' if e.get('highPriority') else 'normal'
        ident = f"OFF-{e['id']}"
        out.append(row(ident, sport, lg if lg != 'NCAAF' else 'NCAAF (ACC)', season_type, e['date'], start,
                       minutes, e.get('away', ''), e.get('home', ''), priority, True,
                       e.get('sourceUrl') or 'https://www.nfl.com/schedules/',
                       e.get('sourceLabel') or 'Official source',
                       note=f"VERIFIED via {e.get('sourceLabel','official source')}. {e.get('venue','')} {e.get('notes','')}".strip(),
                       flags=['official_overlay'] + (['time_unverified'] if start is None else [])))
        added += 1
    return out, added

def overlay_mlb_2027(rows):
    """Replace our generated Giants/Athletics + marquee rows with the official Stats API extract."""
    path = ROOT / 'data' / 'mlb_2027_bayarea.json'
    if not path.exists():
        return rows, 0
    official = _json.load(open(path))
    bay = official.get('bayAreaGames', [])
    marquee = official.get('marqueeGames', [])
    # drop generated SF/ATH regular/spring/postseason rows (they are covered by the officials)
    def involves_ba(g):
        t = (g['away'] + ' ' + g['home']).lower()
        return ('giants' in t) or ('athletics' in t)
    kept = [g for g in rows if not (g['sport'] == 'MLB' and g['season_type'] in ('regular', 'spring_training', 'postseason', 'all_star') and involves_ba(g) and not g['verified'])]
    kept = [g for g in kept if g['id'] != 'MLB-2027-OPEN-NIGHT']
    dropped = len(rows) - len(kept)
    out = list(kept)
    for g in bay + marquee:
        phase = g.get('phase', '')
        gt = g.get('gameType', '')
        if 'Spring Training' in phase or gt == 'S': season_type = 'spring_training'; minutes = DUR['MLB_spring']
        elif gt == 'A' or 'All-Star' in phase: season_type = 'all_star'; minutes = DUR['MLB_allstar']
        elif gt == 'P' or 'Postseason' in phase: season_type = 'postseason'; minutes = DUR['MLB_postseason']
        else: season_type = 'regular'; minutes = DUR['MLB_regular']
        # parse PT directly from utc timestamp when possible (PDT, UTC-7 for Mar-Sep 2027)
        start = None
        if not g.get('startTimeTBD') and g.get('utc'):
            try:
                import datetime as _dt
                utc = _dt.datetime.fromisoformat(g['utc'].replace('Z', '+00:00'))
                pt = utc - _dt.timedelta(hours=7)  # PDT in Mar-Oct 2027 (standard approximation; flagged)
                start = pt.strftime('%H:%M')
            except Exception:
                start = None
        out.append(row(f"MLB27-{g['gamePk']}", 'MLB', 'MLB', season_type, g['date'], start,
                       minutes, g.get('awayName', ''), g.get('homeName', ''),
                       'high' if g.get('highPriority') else 'normal', True,
                       g.get('sourceUrl') or 'https://portal.mlb.com/gameday',
                       'MLB Stats API (statsapi.mlb.com) — verified 2026-11-25',
                       note=f"{g.get('phase','')} · {g.get('venue','')} · gamePk {g.get('gamePk')}. PT converted from UTC (PDT); verify on MLB.com.",
                       flags=['official_overlay'] + (['time_unverified'] if g.get('startTimeTBD') else ['pt_from_utc'])))
    return out, dropped

def overlay_ww1(rows):
    """Replace hardcoded WW1 list with the verified 2026-11-25 capture (38 broadcasts)."""
    path = ROOT / 'data' / 'westwood_one_2026.json'
    if not path.exists():
        return rows, 0
    kept = [g for g in rows if g['sport'] != 'WW1']
    data = _json.load(open(path)).get('broadcasts', [])
    for i, b in enumerate(data):
        kickoff = b.get('kickoffPST') or b.get('airTimePST')
        start = mins_to_hhmm(parse_pst(kickoff))
        priority = 'high' if b.get('is49ers') else 'normal'
        out = row(f"WW1-{i+1:03d}", 'WW1', 'Westwood One Sports · NFL', 'regular', b['date'], start,
                  DUR['NFL'], b.get('matchup', '').split(' at ')[0] if ' at ' in b.get('matchup', '') else b.get('matchup', ''),
                  b.get('matchup', '').split(' at ')[-1] if ' at ' in b.get('matchup', '') else '',
                  priority, True,
                  b.get('sourceUrl') or 'https://www.westwoodonesports.com/nfl-schedule/',
                  'westwoodonesports.com (official) — captured 2026-11-25',
                  note=f"{b.get('broadcastLabel','')} · {b.get('week','')} · pregame {b.get('airTimePST','?')} · {b.get('venue','')} · SF: {b.get('sfAffiliate','')}",
                  flags=['ww1_national', 'official_overlay'] + (['49ers'] if b.get('is49ers') else []))
        kept.append(out)
    return kept, len(kept)

def overlay_ncaaf(year, rows):
    """Fold verified Stanford/Cal rows in (dates verified; times TBD where absent)."""
    path = ROOT / 'data' / 'ncaaf_stanford_cal.json'
    if not path.exists():
        return rows, 0
    games = _json.load(open(path)).get('verifiedGames', [])
    official = [g for g in games if g['date'].startswith(str(year))]
    if not official:
        return rows, 0
    def involves_program(g):
        t = (g['away'] + ' ' + g['home']).lower()
        return ('stanford' in t) or ('california' in t) or ('cal ' in t) or ('cardinal' in t) or ('golden bears' in t)
    out = list(rows)
    for g in official:
        team = g.get('team', '')
        is_stanford = 'Stanford' in team
        marker = 'Stanford' if is_stanford else 'California'
        # drop our generated rows for that program on the same date
        out = [r for r in out if not (r['date'] == g['date'] and marker in (r['away'] + ' ' + r['home']) and 'official_overlay' not in r['flags'])]
        start = None if g.get('startTimeTBD') else mins_to_hhmm(g.get('startMinPST') or parse_pst(g.get('officialTimePST')))
        minutes = DUR['NCAAF']
        away, home = (g.get('matchup') or f"{g.get('opponent','')} at {team}").split(' at ') if ' at ' in (g.get('matchup') or '') else (g.get('opponent', ''), team)
        out.append(row(f"NCAAF-OFF-{g['date']}-{'STAN' if is_stanford else 'CAL'}", 'NCAAF', 'NCAAF (ACC)', 'regular',
                       g['date'], start, minutes, away.replace(' (Week 0)', '').strip(), home.replace(' (Legends Trophy)', '').strip(),
                       'high', True, g.get('sourceUrl') or 'https://theacc.com/',
                       g.get('sourceLabel') or 'Stanford/Cal official',
                       note=f"{g.get('phase','')} · {g.get('venue','')} · radio: {g.get('radio','')}. {g.get('status')}.",
                       flags=['official_overlay'] + (['time_unverified'] if start is None else [])))
    return out, len(official)

def overlay(year, rows):
    rows, n1 = overlay_all_events_verified(year, rows)
    if year == 2027:
        rows, n2 = overlay_mlb_2027(rows)
    else:
        n2 = 0
    rows = overlay_ww1(rows)[0]
    rows, n3 = overlay_ncaaf(year, rows)
    return rows

def global_dedup(rows):
    seen = {}
    for g in rows:
        key = (g['sport'],) + nkey(g['date'], g['away'], g['home'])
        prev = seen.get(key)
        if prev is None:
            seen[key] = g; continue
        keep = prev
        if (g['verified'], g['priority'] == 'high') > (prev['verified'], prev['priority'] == 'high'):
            keep = g
        seen[key] = keep
    return list(seen.values())

if __name__ == "__main__":
    main()
