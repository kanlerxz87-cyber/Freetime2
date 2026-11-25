#!/usr/bin/env python3
"""Build the Free Time Vacation planner data (session 7d4f79aa).

Inputs  : planner/data/raw/*  (official data fetched by .github/workflows/planner-data.yml)
          + the small curated lists below (each transcribed from an official page that is linked per row)
Outputs : planner/data/events.json, estimates.json, days.json, windows.json, meta.json

Rules (from the user's brief):
  * A minute is BUSY when any core event is on air: all 30 MLB clubs (spring training, exhibitions,
    regular season, All-Star Game, postseason), all NFL games (49ers + every Westwood One national
    radio game + the rest of the league, preseason through Super Bowl), Stanford and Cal football.
  * Extended Bay Area radio sports (Warriors, Cal/Stanford men's basketball, Earthquakes, Westwood One
    national college games) are a separate, optional layer.
  * Official values are never altered. TBD start times get a labelled planner estimate (q="T").
    Seasons that are not published yet get labelled season-pattern estimates (q="E").
"""
import json
import os
import re
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = os.path.join(ROOT, "planner", "data", "raw")
OUT = os.path.join(ROOT, "planner", "data")
PT = ZoneInfo("America/Los_Angeles")
ET = ZoneInfo("America/New_York")
UTC = timezone.utc
START, END = date(2026, 11, 25), date(2029, 12, 31)
GENERATED = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
GIANTS, ATHLETICS = 137, 133

# ------------------------------------------------------------------ durations (minutes)
dur_reg = json.load(open(os.path.join(RAW, "mlb_duration_2026_regular.json")))
dur_post = json.load(open(os.path.join(RAW, "mlb_duration_2026_postseason.json")))
DUR = {
    "MLB_R": round(dur_reg["mean_nine_inning"]), "MLB_POST": round(dur_post["mean_nine_inning"]),
    "MLB_S": round(dur_reg["mean_nine_inning"]), "MLB_A": 180,
    "NFL": 185, "NFL_POST": 195, "NFL_SB": 225, "W1_LEAD": 45,
    "NCAAF": 205, "NBA": 135, "NCAAB": 120, "MLS": 115,
}
DUR_NOTES = [
    {"item": "MLB regular season (9 innings)", "minutes": DUR["MLB_R"], "basis": "Mean official time of game, %d nine-inning 2026 games (MLB Stats API gameDurationMinutes, computed by this build)" % dur_reg["nine_inning_games"], "official": True, "src": dur_reg["source"]},
    {"item": "MLB regular season (all games incl. extras)", "minutes": dur_reg["mean_all"], "basis": "Same feed, %d games" % dur_reg["games_with_duration"], "official": True, "src": dur_reg["source"]},
    {"item": "MLB postseason (9 innings)", "minutes": DUR["MLB_POST"], "basis": "Mean of %d nine-inning 2026 postseason games (MLB Stats API)" % dur_post["nine_inning_games"], "official": True, "src": dur_post["source"]},
    {"item": "MLB 2025 average (MLB.com)", "minutes": 158, "basis": "MLB.com: nine-inning games averaged 2 hours, 38 minutes in 2025", "official": True, "src": "https://www.mlb.com/news/mlb-average-game-time-under-three-hours-third-straight-year"},
    {"item": "MLB spring training", "minutes": DUR["MLB_S"], "basis": "No official spring average found; regular-season mean used (estimate)", "official": False, "src": ""},
    {"item": "NFL regular season", "minutes": DUR["NFL"], "basis": "Third-party averages 3:03 (2025) to 3:12 (2024); NFL publishes no official figure that was found. Halftime is inside this time.", "official": False, "src": ""},
    {"item": "NFL postseason / Super Bowl", "minutes": "%d / %d" % (DUR["NFL_POST"], DUR["NFL_SB"]), "basis": "Estimate: extra commercial time; Super Bowl halftime show ~25-30 min", "official": False, "src": ""},
    {"item": "Westwood One pregame lead", "minutes": DUR["W1_LEAD"], "basis": "Westwood One lists on-air times 15-75 min before NFL kickoffs (e.g. 49ers Dec 17: 7:30 PM ET on W1 vs 5:15 PM PT kickoff on 49ers.com). Unconfirmed kickoffs use on-air time + 45 min.", "official": False, "src": "https://www.westwoodonesports.com/nfl-schedule/"},
    {"item": "College football (FBS)", "minutes": DUR["NCAAF"], "basis": "Third-party averages 3:20-3:27; 20-minute halftime is inside this time", "official": False, "src": ""},
    {"item": "NBA", "minutes": DUR["NBA"], "basis": "Third-party report of NBA average ~2:15 (15-minute halftime inside)", "official": False, "src": ""},
    {"item": "College basketball", "minutes": DUR["NCAAB"], "basis": "Estimate (third-party ~2:00-2:06)", "official": False, "src": ""},
    {"item": "MLS", "minutes": DUR["MLS"], "basis": "2 x 45 min + 15 min halftime + ~10 min stoppage (estimate)", "official": False, "src": ""},
]

EVENTS = []      # verified rows (q = "O" official time, "T" official date + estimated time)
ESTIMATES = []   # season-pattern blocks (q = "E")
FLAGS = []
SOURCES = {}


def src(key, url, label, official=True, note=""):
    SOURCES[key] = {"url": url, "label": label, "official": official, "note": note}
    return url


def m(dt):
    """aware datetime -> epoch minutes"""
    return int(dt.astimezone(UTC).timestamp() // 60)


def at(d, hh, mm, tz):
    return datetime(d.year, d.month, d.day, hh, mm, tzinfo=tz)


def add(cat, layer, prio, title, start_dt, dur, q, url, kind, radio="", note="", kick_dt=None, extra=None):
    ev = {"c": cat, "l": layer, "p": prio, "t": title, "s": m(start_dt), "e": m(kick_dt or start_dt) + dur,
          "q": q, "u": url, "g": kind}
    if kick_dt is not None and m(kick_dt) != m(start_dt):
        ev["k"] = m(kick_dt)
    if radio:
        ev["r"] = radio
    if note:
        ev["n"] = note
    if extra:
        ev.update(extra)
    EVENTS.append(ev)
    return ev


def est(cat, layer, title, d, h1, m1, h2, m2, basis, url="", prio="C"):
    s = at(d, h1, m1, PT)
    e = at(d, h2, m2, PT) if (h2, m2) > (h1, m1) else at(d + timedelta(days=1), h2, m2, PT)
    ESTIMATES.append({"c": cat, "l": layer, "p": prio, "t": title, "s": m(s), "e": m(e), "q": "E", "u": url, "n": basis})


# ------------------------------------------------------------------ MLB (official MLB Stats API)
mlb = json.load(open(os.path.join(RAW, "mlb_games.json")))
teams = {t["id"]: t for t in json.load(open(os.path.join(RAW, "mlb_teams.json")))["teams"]}
src("mlb_api", "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2027-01-01&endDate=2027-12-31", "MLB Stats API schedule feed (official MLB data)")
src("mlb_teams", "https://statsapi.mlb.com/api/v1/teams?sportId=1", "MLB Stats API teams (30 clubs)")
GT = {"S": "Spring Training", "E": "Exhibition", "R": "Regular Season", "A": "All-Star Game", "F": "Wild Card",
      "D": "Division Series", "L": "LCS", "W": "World Series"}
mlb_radio_rows = 0
for g in mlb["games"]:
    if (g.get("state") or "").lower() in ("cancelled", "postponed"):
        continue
    utc = datetime.strptime(g["utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    tz = ZoneInfo(g.get("venueTz") or "America/New_York")
    q, note = "O", ""
    if g["tbd"]:
        d = date.fromisoformat(g["date"])
        if g["type"] in ("S", "E"):
            hh, mm = 13, 5
        elif g["type"] == "A":
            hh, mm, tz = 17, 0, PT
        elif d.weekday() >= 5:
            hh, mm = 13, 10
        else:
            hh, mm = 19, 5
        utc = at(d, hh, mm, tz)
        q, note = "T", "Start time TBD in the official schedule; planner estimate (%s %02d:%02d venue time)" % ("weekend" if d.weekday() >= 5 else "weekday", hh, mm)
    dur = DUR["MLB_POST"] if g["type"] in "FDLW" else (DUR["MLB_A"] if g["type"] == "A" else DUR["MLB_R"])
    prio = "H" if GIANTS in (g["home"], g["away"]) or ATHLETICS in (g["home"], g["away"]) else "C"
    radio = ", ".join("%s (%s)" % (b["name"], b["homeAway"]) for b in g.get("radio") or [])
    mlb_radio_rows += 1 if radio else 0
    title = g["desc"] if g["type"] == "A" else "%s @ %s" % (g["awayName"], g["homeName"])
    add("MLB", "core", prio, title, utc, dur, q, "https://www.mlb.com/gameday/%d" % g["pk"], GT.get(g["type"], g["type"]),
        radio=radio, note=note, extra={"v": g.get("venue") or "", "h": g["home"], "a": g["away"]})

# ------------------------------------------------------------------ NFL – 49ers (official 49ers.com)
def tokens(fname):
    raw = open(os.path.join(RAW, "pages", fname)).read().replace("\xa0", " ")
    return [re.sub(r"\s+", " ", t).strip() for t in raw.replace("\n", "|").split("|") if t.strip()]


niners_url = src("niners", "https://www.49ers.com/schedule/", "49ers.com official schedule (times PT, radio KSAN/KNBR)")
tk = tokens("niners_schedule.txt")
niner_games = {}
for i, t in enumerate(tk):
    mt = re.match(r"WEEK (\d+) · (\w{3}) (\d{2})/(\d{2}) · (\d{1,2}):(\d{2}) (AM|PM) PST", t)
    if not mt:
        continue
    wk, mo, dy = int(mt.group(1)), int(mt.group(3)), int(mt.group(4))
    hh = int(mt.group(5)) % 12 + (12 if mt.group(7) == "PM" else 0)
    yr = 2026 if mo >= 8 else 2027
    kick = at(date(yr, mo, dy), hh, int(mt.group(6)), PT)
    vs, opp, tv, radio = tk[i + 1], tk[i + 3], tk[i + 4], tk[i + 5]
    title = ("%s at San Francisco 49ers" % opp) if vs == "VS" else ("San Francisco 49ers at %s" % opp)
    niner_games[kick.date()] = add("NFL", "core", "H", title, kick, DUR["NFL"], "O", niners_url,
                                   "Regular Season (Week %d)" % wk, radio=radio, kick_dt=kick, extra={"tv": tv})
if any(t.startswith("WEEK 18 · TBD") for t in tk):
    FLAGS.append({"id": "N1", "sev": "info", "title": "49ers Week 18 at Arizona: date and time TBD",
                  "detail": "49ers.com lists Week 18 at the Cardinals as TBD. NFL.com says Week 18 is January 9-10, 2027. The planner marks both days busy (estimate).",
                  "links": [niners_url, "https://www.nfl.com/news/2026-27-national-football-league-important-dates"]})
    for d in (date(2027, 1, 9), date(2027, 1, 10)):
        est("NFL", "core", "49ers at Cardinals (Week 18) – date/time TBD", d, 10, 0, 20, 30,
            "Week 18 is Jan 9-10 per NFL.com; exact slot set after Week 17", niners_url, prio="H")

# ------------------------------------------------------------------ NFL – Westwood One national radio (official network schedule)
w1_url = src("w1_nfl", "https://www.westwoodonesports.com/nfl-schedule/", "Westwood One Sports NFL schedule (national radio; times ET = on-air)")
MON = {m_: i + 1 for i, m_ in enumerate(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"])}


def parse_w1(fname, season_start_month):
    tk = tokens(fname)
    out = []
    i = 0
    while i < len(tk) - 3:
        if re.fullmatch(r"[A-Z]{3} \d{2}", tk[i]) and tk[i] == tk[i + 1] and tk[i][:3] in MON:
            mo, dy = MON[tk[i][:3]], int(tk[i][4:])
            title = tk[i + 2]
            j = i + 3
            venue = ""
            if not re.match(r"\d{1,2}:\d{2} (AM|PM) ET", tk[j]):
                venue, j = tk[j], j + 1
            mt = re.match(r"(\d{1,2}):(\d{2}) (AM|PM) ET(?: // (.*))?", tk[j])
            if mt:
                yr = 2026 if mo >= season_start_month else 2027
                hh = int(mt.group(1)) % 12 + (12 if mt.group(3) == "PM" else 0)
                out.append({"date": date(yr, mo, dy), "title": title, "venue": venue,
                            "air": at(date(yr, mo, dy), hh, int(mt.group(2)), ET), "label": (mt.group(4) or "").strip()})
            i = j + 1
        else:
            i += 1
    return out


w1 = parse_w1("w1_grid_nfl.txt", 8)
w1_count = 0
for g in w1:
    w1_count += 1
    nine = niner_games.get(g["air"].astimezone(PT).date())
    if nine and "49ers" in g["title"]:
        nine["s"] = min(nine["s"], m(g["air"]))
        nine["r"] = nine.get("r", "") + "; Westwood One national (on air %s ET)" % g["air"].strftime("%-I:%M %p")
        nine["w1"] = w1_url
        continue
    kick_est = g["air"] + timedelta(minutes=DUR["W1_LEAD"])
    dur = DUR["NFL"]
    add("NFL", "core", "C", g["title"], g["air"], dur, "O", w1_url, g["label"] or "Westwood One national",
        radio="Westwood One Sports national radio (SF affiliates KNBR 680/104.5, KTCT 1050 per station finder)",
        note="Official on-air time from Westwood One; game end estimated from on-air time + %d min pregame + %d min game" % (DUR["W1_LEAD"], dur),
        kick_dt=kick_est, extra={"v": g["venue"]})

# Sunday afternoon slates (non-national games, per-game times not loaded from an official source)
nfl_dates_url = src("nfl_dates", "https://www.nfl.com/news/2026-27-national-football-league-important-dates", "NFL.com 2026-27 important dates (official)")
for d in [date(2026, 11, 29), date(2026, 12, 6), date(2026, 12, 13), date(2026, 12, 20), date(2026, 12, 27), date(2027, 1, 3), date(2027, 1, 10)]:
    est("NFL", "core", "NFL Sunday afternoon games (regional slate)", d, 10, 0, 16, 35,
        "Sunday 10:00 AM and 1:05/1:25 PM PT kickoff windows; per-game times from NFL.com were not retrievable (page is script-rendered)", nfl_dates_url)
FLAGS.append({"id": "N2", "sev": "review", "title": "Non-national NFL Sunday games: per-game times not loaded",
              "detail": "NFL.com schedule pages are rendered by JavaScript and returned no game data to the fetcher. Sunday afternoon regional games (Nov 29 - Jan 10) are shown as an estimated 10:00 AM - 4:35 PM PT block. Every national radio game (Westwood One) and every 49ers game uses official times.",
              "links": ["https://www.nfl.com/schedules/2026/REG13/", nfl_dates_url]})

# 2026-27 postseason: official dates (NFL.com), times not yet set
PO = [(date(2027, 1, 16), "Wild Card Weekend (Sat)", (13, 0, 21, 0)), (date(2027, 1, 17), "Wild Card Weekend (Sun)", (9, 30, 21, 0)),
      (date(2027, 1, 18), "Wild Card Weekend (Mon)", (16, 30, 20, 45)), (date(2027, 1, 23), "Divisional Playoffs (Sat)", (13, 0, 21, 0)),
      (date(2027, 1, 24), "Divisional Playoffs (Sun)", (11, 30, 19, 30)), (date(2027, 1, 31), "AFC and NFC Championship Games", (11, 30, 19, 30))]
for d, t, (a, b, c, e_) in PO:
    est("NFL", "core", t + " – official date, times TBD", d, a, b, c, e_, "Date official (NFL.com); kickoff times TBD - planner estimate", nfl_dates_url, prio="H")
est("NFL", "core", "Super Bowl LXI (SoFi Stadium) – official date, kickoff TBD", date(2027, 2, 14), 14, 0, 19, 45,
    "Date official (NFL.com); ~3:30 PM PT kickoff and Westwood One pregame are estimates", nfl_dates_url, prio="H")
src("nfl_probowl", "https://www.nfl.com/news/nfl-elevates-pro-bowl-selection-game-s-will-cease-being-contested", "NFL.com: AFC-NFC Pro Bowl game no longer staged (Aug 2026)")

# ------------------------------------------------------------------ NCAAF – Stanford & Cal (official athletics sites)
stan_url = src("stanford_fb", "https://gostanford.com/sports/football/schedule", "GoStanford.com 2026 football schedule (official)")
cal_url = src("cal_fb", "https://calbears.com/sports/football/schedule/text", "CalBears.com 2026 football schedule (official)")
src("stanford_radio", "https://gostanford.com/news/2026/07/30/2026-football-radio-broadcast-team-announced", "GoStanford.com: 2026 football radio on KNBR/KTCT 1050 AM")
lines = open(os.path.join(RAW, "pages", "stanford_fb.txt")).read().split("\n")
seen = set()
for i, ln in enumerate(lines):
    mt = re.match(r"\s*(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (Nov|Dec|Jan) (\d{1,2}) (\d{1,2}):(\d{2}) (AM|PM)", ln)
    if not mt:
        continue
    mo = MON[mt.group(2).upper()]
    d = date(2026 if mo >= 8 else 2027, mo, int(mt.group(3)))
    if d < START or d in seen:
        continue
    nxt = [l.strip() for l in lines[i + 1:i + 8] if l.strip()]
    opp = next((l for l in nxt if re.match(r"(vs\.|at) \S", l)), "")
    hh = int(mt.group(4)) % 12 + (12 if mt.group(6) == "PM" else 0)
    seen.add(d)
    add("NCAAF", "core", "H", (opp[4:] + " at Stanford" if opp.startswith("vs. ") else "Stanford " + opp), at(d, hh, int(mt.group(5)), PT), DUR["NCAAF"], "O", stan_url,
        "Regular season", radio="KNBR/KTCT 1050 AM (Stanford radio home per GoStanford.com); KZSU 90.1 FM")
caltxt = "|".join(tokens("cal_fb_text.txt"))
for mt in re.finditer(r"(\w{3}) (\d{1,2}) \((\w{3})\)\|(\d{1,2}):(\d{2}) (AM|PM)\|(Home|Away|Neutral)\|([^|]+)\|", caltxt):
    mo = MON[mt.group(1).upper()]
    d = date(2026 if mo >= 8 else 2027, mo, int(mt.group(2)))
    if d < START:
        continue
    hh = int(mt.group(4)) % 12 + (12 if mt.group(6) == "PM" else 0)
    title = ("%s at Cal" % mt.group(8)) if mt.group(7) == "Home" else ("Cal at %s" % mt.group(8))
    add("NCAAF", "core", "H", title, at(d, hh, int(mt.group(5)), PT), DUR["NCAAF"], "O", cal_url, "Regular season",
        radio="KSFO 810 AM (Cal Bears radio per CalBears.com schedule)")
FLAGS.append({"id": "C1", "sev": "info", "title": "Stanford bowl game possible (TBD)",
              "detail": "Stanford is 6-5 before its Nov 28 game. A bowl game (mid-December to early January) is possible and is not on any official schedule yet. Days Dec 7, 2026 - Jan 25, 2027 are therefore not certified free for college football until bowl/CFP selections (Dec 6) are checked.",
              "links": [stan_url, "https://collegefootballplayoff.com/sports/2018/8/31/cfp-games-schedule"]})
cal_ucla = src("cal_ucla", "https://calbears.com/news/2024/7/10/football-cal-ucla-schedule-4-games-from-2026-29", "CalBears.com: Cal-UCLA series 2026-29 (official dates)")
for d, t in [(date(2027, 9, 4), "Cal at UCLA (Rose Bowl)"), (date(2028, 9, 2), "UCLA at Cal"), (date(2029, 9, 15), "Cal at UCLA (Rose Bowl)")]:
    add("NCAAF", "core", "H", t, at(d, 12, 30, PT), DUR["NCAAF"], "T", cal_ucla, "Regular season (future)",
        note="Date official (CalBears.com); kickoff TBD - planner estimate 12:30 PM PT")

# ------------------------------------------------------------------ Extended layer
cal_mbb = src("cal_mbb", "https://calbears.com/sports/mens-basketball/schedule/text", "CalBears.com 2026-27 men's basketball schedule (radio KSFO 810 AM)")
txt = "|".join(tokens("cal_mbb.txt"))
for mt in re.finditer(r"(\w{3}) (\d{1,2}) \((\w{3})\)\|(\d{1,2})(?::(\d{2}))? (a\.m\.|p\.m\.) PT[^|]*\|(Home|Away|Neutral)\|([^|]+)\|", txt):
    mo = MON[mt.group(1).upper()]
    d = date(2026 if mo >= 8 else 2027, mo, int(mt.group(2)))
    if d < START:
        continue
    hh = int(mt.group(4)) % 12 + (12 if mt.group(6) == "p.m." else 0)
    opp = mt.group(8)
    title = ("%s at Cal" % opp) if mt.group(7) == "Home" else ("Cal vs %s" % opp if mt.group(7) == "Neutral" else "Cal at %s" % opp)
    add("CBB", "ext", "X", title + " (men's basketball)", at(d, hh, int(mt.group(5) or 0), PT), DUR["NCAAB"], "O", cal_mbb,
        "College basketball", radio="KSFO 810 AM")

stan_mbb = src("stanford_mbb", "https://gostanford.com/sports/mens-basketball/schedule", "GoStanford.com 2026-27 men's basketball schedule (times PT)")
STAN_MBB = [("2026-11-25", "21:00", "Stanford vs Saint Louis (Palm Desert)"), ("2026-11-29", "13:00", "Portland at Stanford"),
            ("2026-12-02", "18:15", "Stanford at Texas A&M"), ("2026-12-06", "13:00", "Pacific at Stanford"),
            ("2026-12-14", "19:00", "Northern Colorado at Stanford"), ("2026-12-18", "19:00", "San Jose State at Stanford"),
            ("2026-12-22", "17:00", "St. Thomas at Stanford"), ("2026-12-30", "11:00", "Stanford at Notre Dame"),
            ("2027-01-02", "15:00", "Stanford at Louisville"), ("2027-01-06", "18:00", "Virginia at Stanford"),
            ("2027-01-09", "14:30", "Florida State at Stanford"), ("2027-01-13", "18:00", "Stanford at Duke"),
            ("2027-01-16", "11:15", "Stanford at North Carolina"), ("2027-01-23", "18:00", "Stanford at California"),
            ("2027-01-27", "20:00", "Syracuse at Stanford"), ("2027-01-30", "17:00", "NC State at Stanford"),
            ("2027-02-03", "16:00", "Stanford at Georgia Tech"), ("2027-02-06", "17:00", "Stanford at SMU"),
            ("2027-02-10", "18:00", "Miami at Stanford"), ("2027-02-13", "13:30", "Virginia Tech at Stanford"),
            ("2027-02-17", "18:00", "Stanford at Syracuse"), ("2027-02-20", "09:00", "Stanford at Clemson"),
            ("2027-02-24", "20:00", "Wake Forest at Stanford"), ("2027-02-27", None, "Boston College at Stanford"),
            ("2027-03-06", "13:00", "California at Stanford")]
for ds, tm, title in STAN_MBB:
    d = date.fromisoformat(ds)
    if tm is None:
        add("CBB", "ext", "X", title + " (men's basketball)", at(d, 17, 0, PT), DUR["NCAAB"], "T", stan_mbb, "College basketball",
            radio="", note="Official page says '5 or 5:30 PM' - start left unconfirmed; planner uses 5:00 PM")
    else:
        hh, mm = map(int, tm.split(":"))
        add("CBB", "ext", "X", title + " (men's basketball)", at(d, hh, mm, PT), DUR["NCAAB"], "O", stan_mbb, "College basketball", radio="")
FLAGS.append({"id": "X1", "sev": "review", "title": "Stanford men's basketball radio station not verified for 2026-27",
              "detail": "GoStanford.com lists games and TV but the fetched page shows no radio station. Older Stanford pages name KNBR 1050; not confirmed for this season. Games are shown, radio is blank.",
              "links": [stan_mbb]})

gsw_url = src("warriors", "https://www.nba.com/team/1610612744/schedule", "NBA.com Warriors schedule (official; captured via search index because NBA blocks automated fetches)")
src("warriors_radio", "https://www.nba.com/warriors/news/warriors-announce-2026-27-television-radio-broadcast-schedules-20260824", "NBA.com/Warriors: 95.7 The Game airs all preseason and regular season games")
GSW = [("2026-11-25", "22:00", "Sacramento Kings at Golden State Warriors"), ("2026-11-27", "21:30", "Golden State Warriors at Portland Trail Blazers"),
       ("2026-11-29", "20:30", "LA Clippers at Golden State Warriors"), ("2026-12-01", "22:00", "Utah Jazz at Golden State Warriors"),
       ("2026-12-12", "20:00", "Golden State Warriors at Cleveland Cavaliers"), ("2026-12-14", "20:00", "Golden State Warriors at Memphis Grizzlies"),
       ("2026-12-16", "19:00", "Golden State Warriors at Indiana Pacers"), ("2026-12-18", "19:30", "Golden State Warriors at Toronto Raptors"),
       ("2026-12-20", "20:00", "Golden State Warriors at Milwaukee Bucks"), ("2026-12-22", "22:30", "Dallas Mavericks at Golden State Warriors"),
       ("2026-12-23", "22:30", "Golden State Warriors at LA Clippers"), ("2026-12-25", "22:30", "Denver Nuggets at Golden State Warriors"),
       ("2026-12-27", "20:30", "Minnesota Timberwolves at Golden State Warriors")]
for ds, tm, title in GSW:
    d = date.fromisoformat(ds)
    hh, mm = map(int, tm.split(":"))
    add("NBA", "ext", "X", title, at(d, hh, mm, ET), DUR["NBA"], "O", gsw_url, "NBA regular season", radio="95.7 The Game (KGMZ-FM)")
FLAGS.append({"id": "X2", "sev": "review", "title": "Warriors schedule after Dec 27, 2026 not loaded",
              "detail": "NBA.com and the official NBA CDN return HTTP 403 to automated requests (GitHub runner). 13 games through Dec 27 were read from NBA.com's own schedule page as captured by a search index. Later games must be checked at nba.com/warriors/schedule.",
              "links": [gsw_url]})

quakes_url = src("quakes", "https://www.sjearthquakes.com/news/san-jose-earthquakes-announce-2027-major-league-soccer-sprint-season-schedule-presented-by-habbas-law", "SJEarthquakes.com 2027 MLS Sprint Season schedule (times PT)")
src("quakes_radio", "https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season", "SJEarthquakes.com: 2026 radio KSFO 810 AM / KZSF 1370 AM")
qt = "|".join(tokens("quakes_2027.txt"))
MONTHS = {n: i + 1 for i, n in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])}
for mt in re.finditer(r"\|(\d{1,2})\|\w+day, (\w+)\.? (\d{1,2}), (\d{4})\|([^|]+)\|(Away|Home)\|(\d{1,2})(?::(\d{2}))? (a\.m\.|p\.m\.)\|([^|]+)\|", qt):
    mon = next(v for k, v in MONTHS.items() if k.startswith(mt.group(2)))
    d = date(int(mt.group(4)), mon, int(mt.group(3)))
    hh = int(mt.group(7)) % 12 + (12 if mt.group(9) == "p.m." else 0)
    title = ("%s at San Jose Earthquakes" % mt.group(5)) if mt.group(6) == "Home" else ("San Jose Earthquakes at %s" % mt.group(5))
    add("MLS", "ext", "X", title, at(d, hh, int(mt.group(8) or 0), PT), DUR["MLS"], "O", quakes_url, "MLS Sprint Season (match %s)" % mt.group(1),
        radio="", note="2027 radio not announced (2026: KSFO 810 AM English, KZSF 1370 AM Spanish)")

w1c_url = src("w1_college", "https://www.westwoodonesports.com/ncaa-football/", "Westwood One Sports NCAA football and basketball broadcasts")
for fname, kind, cat in (("w1_grid_ncaaf.txt", "Westwood One national college football", "W1C"), ("w1_grid_ncaab.txt", "Westwood One national college basketball", "W1C")):
    for g in parse_w1(fname, 8):
        add(cat, "ext", "X", g["title"], g["air"], DUR["NCAAF"] if "football" in kind else DUR["NCAAB"], "O", w1c_url, kind,
            radio="Westwood One Sports (SF affiliates KNBR/KTCT per station finder)")

# ------------------------------------------------------------------ Season-pattern estimates (not yet published)
def first_monday_sept(y):
    d = date(y, 9, 1)
    return d + timedelta(days=(0 - d.weekday()) % 7)


def nfl_season_estimates(y, sb_official=None):
    kick = first_monday_sept(y) + timedelta(days=3)               # Thursday after Labor Day
    hof = kick - timedelta(days=35)
    basis = "NFL %d season not published; pattern of the 2026 season (NFL.com important dates)" % y
    est("NFL", "core", "NFL Hall of Fame Game (estimate)", hof, 17, 0, 20, 30, basis, nfl_dates_url)
    for wk in range(3):
        base = hof + timedelta(days=7 * (wk + 1))
        for off, (a, b, c, d_) in enumerate([(16, 0, 22, 30), (16, 0, 22, 30), (13, 0, 22, 30), (13, 0, 20, 30)]):
            est("NFL", "core", "NFL preseason week %d games (estimate, incl. 49ers)" % (wk + 1), base + timedelta(days=off), a, b, c, d_, basis, nfl_dates_url, prio="H")
    thanks = date(y, 11, 1) + timedelta(days=(3 - date(y, 11, 1).weekday()) % 7 + 21)
    for wk in range(1, 19):
        thu = kick + timedelta(days=7 * (wk - 1))
        sun, mon, sat = thu + timedelta(days=3), thu + timedelta(days=4), thu + timedelta(days=2)
        if wk < 18:
            est("NFL", "core", "Thursday Night Football (estimate)", thu, 16, 30, 20, 30, basis, nfl_dates_url)
            est("NFL", "core", "Monday Night Football (estimate)", mon, 16, 0, 20, 30, basis, nfl_dates_url)
        start_h = (6, 30) if 4 <= wk <= 11 else (10, 0)
        est("NFL", "core", "NFL Sunday slate incl. 49ers & Sunday Night Football (estimate)", sun, start_h[0], start_h[1], 20, 35, basis, nfl_dates_url, prio="H")
        if wk >= 15:
            est("NFL", "core", "NFL Saturday games (estimate)", sat, 13, 0, 20, 30, basis, nfl_dates_url)
    est("NFL", "core", "NFL Thanksgiving games (estimate)", thanks, 9, 30, 20, 30, basis, nfl_dates_url)
    est("NFL", "core", "NFL Black Friday game (estimate)", thanks + timedelta(days=1), 11, 30, 15, 30, basis, nfl_dates_url)
    xmas = date(y, 12, 25)
    est("NFL", "core", "NFL Christmas games (estimate)", xmas, 9, 30, 20, 30, basis, nfl_dates_url)
    w18 = kick + timedelta(days=7 * 17 + 3)
    sb = w18 + timedelta(days=35)
    po = [(6, "Wild Card (Sat)", (13, 0, 21, 0)), (7, "Wild Card (Sun)", (9, 30, 21, 0)), (8, "Wild Card (Mon)", (16, 30, 20, 45)),
          (13, "Divisional (Sat)", (13, 0, 21, 0)), (14, "Divisional (Sun)", (11, 30, 19, 30)), (21, "Conference Championships", (11, 30, 19, 30))]
    for off, t, (a, b, c, d_) in po:
        est("NFL", "core", "NFL %s (estimate)" % t, w18 + timedelta(days=off), a, b, c, d_, basis, nfl_dates_url, prio="H")
    return kick, w18, sb


SB = {}
k27, w27, sb27 = nfl_season_estimates(2027)
SB[2028] = (sb27, True)
sb28_url = src("sb_lxii", "https://www.mercedesbenzstadium.com/events/super-bowl-lxii", "Mercedes-Benz Stadium: Super Bowl LXII, February 13, 2028 (official venue)")
assert sb27 == date(2028, 2, 13), sb27
est("NFL", "core", "Super Bowl LXII (Atlanta) – official date, kickoff TBD", sb27, 14, 0, 19, 45, "Date official (Mercedes-Benz Stadium); kickoff ~3:30 PM PT estimate", sb28_url, prio="H")
k28, w28, sb28 = nfl_season_estimates(2028)
sb29_url = src("sb_lxiii", "https://www.allegiantstadium.com/events/detail/super-bowl-lxiii", "Allegiant Stadium: Super Bowl LXIII 2029, date TBA on the official page")
est("NFL", "core", "Super Bowl LXIII (Las Vegas) – date not official (estimate)", sb28, 14, 0, 19, 45, "Official pages list the date as TBA; Feb %d, 2029 follows the 18-week pattern (estimate)" % sb28.day, sb29_url, prio="H")
SB[2029] = (sb28, False)
k29, w29, sb29 = nfl_season_estimates(2029)
FLAGS.append({"id": "N3", "sev": "review", "title": "Super Bowl LXIII date is not on an official page",
              "detail": "Allegiant Stadium and NFL.com confirm Las Vegas as host but show the date as TBA. The planner uses Sunday, %s (18-week season pattern) as an estimate." % sb28.strftime("%B %-d, %Y"),
              "links": [sb29_url]})

mlb_basis = "MLB %s not published; pattern of the official 2027 schedule (Spring Training Feb 19, Opening Day Mar 25, final day Sep 26)"
src("mlb_spring_2027", "https://www.mlb.com/press-release/press-release-mlb-announces-2027-spring-training-schedule", "MLB.com: 2027 Spring Training begins Friday, February 19")
for d in (date(2027, 9, 28) + timedelta(days=i) for i in range(33)):
    a, b, c, e_ = (10, 0, 21, 30) if d <= date(2027, 10, 9) else (13, 0, 21, 0)
    est("MLB", "core", "MLB postseason games (estimate; 2027 postseason dates not published)", d, a, b, c, e_, mlb_basis % "2027 postseason", "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2027-09-27&endDate=2027-11-15")
for y, st_, od, last, post_end in ((2028, date(2028, 2, 18), date(2028, 3, 23), date(2028, 10, 1), date(2028, 11, 1)),
                                   (2029, date(2029, 2, 16), date(2029, 3, 22), date(2029, 9, 30), date(2029, 10, 31))):
    d = st_
    while d <= post_end:
        if d < od:
            est("MLB", "core", "MLB Spring Training (estimate)", d, 10, 0, 21, 0, mlb_basis % str(y), "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=%d-01-01&endDate=%d-12-31" % (y, y))
        elif d <= last:
            est("MLB", "core", "MLB regular season (estimate)", d, 9, 30, 22, 30, mlb_basis % str(y), "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=%d-01-01&endDate=%d-12-31" % (y, y), prio="H")
        else:
            est("MLB", "core", "MLB postseason (estimate)", d, 13, 0, 21, 0, mlb_basis % str(y), "")
        d += timedelta(days=1)
FLAGS.append({"id": "M1", "sev": "review", "title": "MLB 2028 and 2029 schedules not released; 2027 postseason dates not published",
              "detail": "The MLB Stats API returns 0 games for 2028 and 2029 and no 2027 postseason games. The planner uses estimated blocks: Spring Training from Feb 18, 2028 / Feb 16, 2029, regular season to Oct 1, 2028 / Sep 30, 2029, postseason to early November. MLB has proposed a 154-game season from 2029 (a bargaining proposal, not adopted).",
              "links": ["https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2028-01-01&endDate=2028-12-31"]})
FLAGS.append({"id": "M2", "sev": "review", "title": "MLB labor agreement expires Dec 1, 2026",
              "detail": "The 2027 schedule was published pending a new collective bargaining agreement. A lockout could delay Spring Training (Feb 19) or Opening Day (Mar 24/25). That would add free time but cannot be planned on.",
              "links": ["https://www.mlb.com/press-release/press-release-mlb-announces-2027-spring-training-schedule"]})
FLAGS.append({"id": "M3", "sev": "info", "title": "MLB TBD start times use planner estimates",
              "detail": "Many 2027 games (including most Giants home games) are 'start time TBD' in the official feed. The planner estimates 7:05 PM (weekday) or 1:10 PM (weekend) in the venue's time zone, 1:05 PM for Spring Training. These rows are marked EST TIME.",
              "links": [SOURCES["mlb_api"]["url"]]})

cfp = src("cfp", "https://collegefootballplayoff.com/sports/2018/8/31/cfp-games-schedule", "CollegeFootballPlayoff.com future schedules (2027-28 regular season ends Nov 27, 2027)")
for y, first, last in ((2027, date(2027, 8, 28), date(2027, 11, 27)), (2028, date(2028, 8, 26), date(2028, 11, 25)), (2029, date(2029, 8, 25), date(2029, 11, 24))):
    d = first
    while d <= last:
        if not any(e["c"] == "NCAAF" and abs(e["s"] - m(at(d, 12, 0, PT))) < 1440 for e in EVENTS):
            est("NCAAF", "core", "Stanford / Cal football Saturday (estimate; %d schedules not fully published)" % y, d, 12, 30, 16, 0,
                "Saturday pattern; dates/times not published (official CFP calendar ends the 2027 regular season Nov 27)", cfp, prio="H")
        d += timedelta(days=7)

# ------------------------------------------------------------------ Day summaries
def day_bounds(d):
    return m(at(d, 0, 0, PT)), m(at(d + timedelta(days=1), 0, 0, PT))


def union_len(iv):
    iv = sorted(iv)
    tot, cur_s, cur_e = 0, None, None
    for s, e in iv:
        if cur_e is None or s > cur_e:
            if cur_e is not None:
                tot += cur_e - cur_s
            cur_s, cur_e = s, e
        else:
            cur_e = max(cur_e, e)
    if cur_e is not None:
        tot += cur_e - cur_s
    return tot


def mlb_known(d):
    return d <= date(2027, 9, 26)


def nfl_known(d):
    return d <= date(2027, 2, 14) or (date(d.year, 2, 15) <= d <= date(d.year, 7, 15))


CFP_FINAL = {2027: date(2027, 1, 25), 2028: date(2028, 1, 24), 2029: date(2029, 1, 22)}


def ncaaf_known(d):
    if d <= date(2026, 12, 6):
        return True
    f = CFP_FINAL.get(d.year)
    return bool(f) and f < d <= date(d.year, 8, 15)


allrows = EVENTS + ESTIMATES
by_day = {}
for idx, ev in enumerate(allrows):
    s_d = datetime.fromtimestamp(ev["s"] * 60, UTC).astimezone(PT).date()
    e_d = datetime.fromtimestamp((ev["e"] - 1) * 60, UTC).astimezone(PT).date()
    d = s_d
    while d <= e_d:
        by_day.setdefault(d, []).append(idx)
        d += timedelta(days=1)

DAYS = []
d = START
while d <= END:
    a, b = day_bounds(d)
    core_iv, ext_iv, cnt, hi, ver, est_any = [], [], {}, 0, False, False
    for idx in by_day.get(d, []):
        ev = allrows[idx]
        s, e = max(ev["s"], a), min(ev["e"], b)
        if e <= s:
            continue
        starts_today = a <= ev["s"] < b
        if ev["l"] == "core":
            core_iv.append((s, e))
            if starts_today:
                cnt[ev["c"]] = cnt.get(ev["c"], 0) + 1
                hi += 1 if ev["p"] == "H" else 0
            if ev["q"] == "E":
                est_any = True
            else:
                ver = True
        else:
            ext_iv.append((s, e))
            if starts_today:
                cnt["X"] = cnt.get("X", 0) + 1
    busy = union_len(core_iv)
    if ver:
        st = "B"
    elif est_any:
        st = "b"
    elif mlb_known(d) and nfl_known(d) and ncaaf_known(d):
        st = "F"
    else:
        st = "f"
    DAYS.append({"d": d.isoformat(), "s": st, "b": busy, "m": b - a, "x": union_len(core_iv + ext_iv), "n": cnt, "h": hi})
    d += timedelta(days=1)

# ------------------------------------------------------------------ Vacation windows
day_index = {x["d"]: x for x in DAYS}


def core_events_between(d1, d2):
    a, _ = day_bounds(d1)
    _, b = day_bounds(d2)
    hits = [ev for ev in allrows if ev["l"] == "core" and ev["s"] < b and ev["e"] > a]
    return hits


def ext_events_between(d1, d2):
    a, _ = day_bounds(d1)
    _, b = day_bounds(d2)
    return [ev for ev in allrows if ev["l"] == "ext" and ev["s"] < b and ev["e"] > a]


def summarize(evs):
    out, seen_t = [], set()
    for ev in sorted(evs, key=lambda e: e["s"]):
        key = (ev["t"], ev["s"])
        if key in seen_t:
            continue
        seen_t.add(key)
        out.append({"t": ev["t"], "s": ev["s"], "e": ev["e"], "q": ev["q"], "c": ev["c"], "p": ev["p"], "u": ev.get("u", "")})
    return out


WINDOWS = {}
for y in (2027, 2028, 2029):
    yd = [x for x in DAYS if x["d"].startswith(str(y))]
    res = {"best": {}, "runs": []}
    for L in (7, 14, 21):
        best = None
        for i in range(len(yd) - L + 1):
            span = yd[i:i + L]
            busy = sum(x["b"] for x in span)
            hi = sum(x["h"] for x in span)
            unver = sum(1 for x in span if x["s"] in "fb")
            key = (busy, hi, unver, i)
            if best is None or key < best[0]:
                best = (key, span)
        span = best[1]
        d1, d2 = date.fromisoformat(span[0]["d"]), date.fromisoformat(span[-1]["d"])
        evs = summarize(core_events_between(d1, d2))
        res["best"][str(L)] = {"start": span[0]["d"], "end": span[-1]["d"], "busy_min": best[0][0], "events": evs,
                               "verified_days": sum(1 for x in span if x["s"] in "FB"), "days": L,
                               "ext": len(summarize(ext_events_between(d1, d2)))}
    run = []
    for x in yd + [{"d": "", "s": "B", "b": 1}]:
        if x["b"] == 0 and x["s"] in "Ff":
            run.append(x)
        else:
            if len(run) >= 3:
                res["runs"].append({"start": run[0]["d"], "end": run[-1]["d"], "days": len(run),
                                    "verified": all(r["s"] == "F" for r in run),
                                    "ext": len(summarize(ext_events_between(date.fromisoformat(run[0]["d"]), date.fromisoformat(run[-1]["d"]))))})
            run = []
    res["runs"].sort(key=lambda r: (-r["days"], r["start"]))
    res["free_days"] = sum(1 for x in yd if x["b"] == 0 and x["s"] in "Ff")
    res["verified_free_days"] = sum(1 for x in yd if x["s"] == "F")
    res["single_free_days"] = [x["d"] for x in yd if x["b"] == 0 and x["s"] in "Ff"]
    WINDOWS[str(y)] = res

# ------------------------------------------------------------------ Radio reference (Outer Sunset, SF 94122)
RADIO = [
    {"freq": "680 AM", "call": "KNBR", "role": "Giants flagship (official MLB feed lists KNBR 680 on Giants games); 49ers co-flagship; Westwood One Sports affiliate", "src": "https://www.49ers.com/schedule/", "src2": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId=137&startDate=2026-09-25&endDate=2026-09-27&hydrate=broadcasts(all)"},
    {"freq": "104.5 FM", "call": "KNBR-FM", "role": "Simulcast of KNBR 680; 49ers co-flagship (49ers.com lists KNBR 104.5 FM)", "src": "https://www.49ers.com/schedule/", "src2": "https://www.westwoodonesports.com/station-finder/"},
    {"freq": "107.7 FM", "call": "KSAN", "role": "49ers co-flagship (49ers.com lists KSAN 107.7 FM on every game)", "src": "https://www.49ers.com/schedule/", "src2": ""},
    {"freq": "1050 AM", "call": "KTCT", "role": "Stanford football (KNBR/KTCT 1050 AM, GoStanford.com); Westwood One affiliate (NFL, college, U.S. Soccer)", "src": "https://gostanford.com/news/2026/07/30/2026-football-radio-broadcast-team-announced", "src2": "https://www.westwoodonesports.com/station-finder/"},
    {"freq": "810 AM", "call": "KSFO", "role": "Cal football and men's basketball (CalBears.com 'Radio: KSFO 810 AM'); Earthquakes English 2026", "src": "https://calbears.com/sports/football/schedule", "src2": "https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season"},
    {"freq": "95.7 FM", "call": "KGMZ-FM", "role": "Warriors flagship, all preseason and regular season games (NBA.com/Warriors)", "src": "https://www.nba.com/warriors/news/warriors-announce-2026-27-television-radio-broadcast-schedules-20260824", "src2": ""},
    {"freq": "960 AM", "call": "KNEW", "role": "Athletics 'Bay Area' affiliate on MLB.com's A's affiliates page; NOT listed on game-level broadcast data (flag R1)", "src": "https://www.mlb.com/athletics/schedule/affiliates", "src2": ""},
    {"freq": "650 AM", "call": "KSTE", "role": "Athletics flagship (Sacramento); official MLB feed lists 'Talk 650 KSTE' on A's games; Outer Sunset reception unverified", "src": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId=133&startDate=2026-09-25&endDate=2026-09-27&hydrate=broadcasts(all)", "src2": "https://www.mlb.com/athletics/schedule/affiliates"},
    {"freq": "1510 AM", "call": "KSFN", "role": "Giants Spanish-language radio (official MLB feed)", "src": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId=137&startDate=2026-09-25&endDate=2026-09-27&hydrate=broadcasts(all)", "src2": ""},
    {"freq": "1370 AM", "call": "KZSF", "role": "Earthquakes Spanish-language flagship (2026)", "src": "https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season", "src2": ""},
    {"freq": "90.1 FM", "call": "KZSU", "role": "Stanford student station; Stanford game notes say KZSU carries all Stanford football games; reception in 94122 unverified", "src": "https://godeacs.com/documents/download/2026/9/29/Vy8nqHhsTv4eaBrJnsBsezwFHiyL7Z6mFU1QDuIe.pdf", "src2": ""},
]
FLAGS.append({"id": "R1", "sev": "review", "title": "A's Bay Area radio: KNEW 960 vs game-level data",
              "detail": "MLB.com's Athletics affiliates page lists 960 AM KNEW for the Bay Area, but the official MLB game feed for the last 2026 series lists only Talk 650 KSTE (English), KVMX (Spanish) and A's Cast. Whether every A's game airs on KNEW 960 in San Francisco is not confirmed.",
              "links": ["https://www.mlb.com/athletics/schedule/affiliates", RADIO[7]["src"]]})
FLAGS.append({"id": "R2", "sev": "review", "title": "Reception in the Outer Sunset (94122) not field-tested",
              "detail": "No station's signal strength at 94122 was measured. KNBR-FM and most FM stations transmit from Sutro Tower or San Bruno Mountain; AM reception indoors varies. Treat 'receivable' as unverified.",
              "links": ["https://www.westwoodonesports.com/station-finder/"]})
FLAGS.append({"id": "R3", "sev": "info", "title": "Westwood One station finder tables are labelled 2025",
              "detail": "The station finder lists KNBR-AM, KNBR-FM, KNBR-F2 and KTCT-AM for San Francisco (NFL, NCAA football, NCAA basketball) and KTCT-AM for U.S. Soccer, but the tables are captioned '2025'. W1 also notes not every affiliate airs every broadcast (blackouts/conflicts).",
              "links": ["https://www.westwoodonesports.com/station-finder/"]})
FLAGS.append({"id": "Q1", "sev": "info", "title": "Prior reference sites did not load",
              "detail": "The three earlier sites named in the brief (VacationSchedule, ScheduleFreeTime, RADIOSF on buffedlizard55-lab.github.io) returned errors to the fetch tool and their repositories are not public, so none of their data was reused.",
              "links": ["https://buffedlizard55-lab.github.io/VacationSchedule/site/", "https://buffedlizard55-lab.github.io/ScheduleFreeTime/", "https://buffedlizard55-lab.github.io/RADIOSF/"]})
FLAGS.append({"id": "Q2", "sev": "review", "title": "Other sessions' 2027 window omits the Feb 1-13 gap and calls 2027 Spring Training unreleased",
              "detail": "data/windows_2026_2029.json (session b1591c47) gives the 2027 strict window as Feb 15-18 with an 'ESTIMATED' Spring Training start. MLB published the 2027 Spring Training schedule (Feb 19) and the NFL has no games between the Conference Championships (Jan 31) and the Super Bowl (Feb 14); the AFC-NFC Pro Bowl game is no longer staged. Under the brief's definition Feb 1-13, 2027 is free. That file belongs to another session and was not edited.",
              "links": ["https://www.mlb.com/press-release/press-release-mlb-announces-2027-spring-training-schedule", nfl_dates_url, "https://www.nfl.com/news/nfl-elevates-pro-bowl-selection-game-s-will-cease-being-contested"]})
FLAGS.append({"id": "Q3", "sev": "info", "title": "Westwood One times vs NFL kickoff times (explains earlier flag F1)",
              "detail": "Westwood One lists on-air times (e.g. TNF 7:30 PM ET, MNF 7:00 PM ET, SNF 7:30 PM ET) while NFL/team sites list kickoffs (8:15, 8:15, 8:20 PM ET). The gap matches the radio pregame. The planner treats the W1 time as the start of air time and the team-site kickoff (when known) for the game end.",
              "links": [w1_url, niners_url]})

# ------------------------------------------------------------------ Write
os.makedirs(OUT, exist_ok=True)
EVENTS.sort(key=lambda e: (e["s"], e["c"]))
ESTIMATES.sort(key=lambda e: (e["s"], e["c"]))
for i, ev in enumerate(EVENTS):
    ev["i"] = i


def dump(name, obj):
    with open(os.path.join(OUT, name), "w") as f:
        json.dump(obj, f, separators=(",", ":"), ensure_ascii=False)


dump("events.json", {"generated": GENERATED, "events": EVENTS})
dump("estimates.json", {"generated": GENERATED, "estimates": ESTIMATES})
dump("days.json", {"generated": GENERATED, "start": START.isoformat(), "end": END.isoformat(), "days": DAYS})
dump("windows.json", {"generated": GENERATED, "windows": WINDOWS})
mlb_counts = {}
for ev in EVENTS:
    if ev["c"] == "MLB":
        for tid in (ev.get("h"), ev.get("a")):
            if tid in teams:
                mlb_counts.setdefault(tid, {"S": 0, "E": 0, "R": 0, "TBD": 0})
                key = {"Spring Training": "S", "Exhibition": "E", "Regular Season": "R"}.get(ev["g"])
                if key:
                    mlb_counts[tid][key] += 1
                if ev["q"] == "T":
                    mlb_counts[tid]["TBD"] += 1
team_rows = sorted(({"id": t["id"], "name": t["name"], "abbr": t.get("abbreviation"), "league": (t.get("league") or {}).get("name"),
                     "division": (t.get("division") or {}).get("name"), "counts": mlb_counts.get(t["id"], {}),
                     "high": t["id"] in (GIANTS, ATHLETICS)} for t in teams.values()), key=lambda r: (not r["high"], r["name"]))
dump("meta.json", {"generated": GENERATED, "session": "7d4f79aa", "durations": DUR, "duration_notes": DUR_NOTES,
                   "teams": team_rows, "flags": FLAGS, "sources": SOURCES, "radio": RADIO,
                   "counts": {"events": len(EVENTS), "estimates": len(ESTIMATES), "mlb": sum(1 for e in EVENTS if e["c"] == "MLB"),
                              "mlb_tbd": sum(1 for e in EVENTS if e["c"] == "MLB" and e["q"] == "T"), "w1_nfl": w1_count,
                              "mlb_with_radio": mlb_radio_rows},
                   "fetch_log": json.load(open(os.path.join(RAW, "fetch_log.json")))})
print("events", len(EVENTS), "estimates", len(ESTIMATES), "days", len(DAYS), "w1", w1_count, "mlb_radio", mlb_radio_rows)
for y, r in WINDOWS.items():
    print(y, "free_days", r["free_days"], "verified", r["verified_free_days"], "runs", [(x["start"], x["end"], x["days"], x["verified"]) for x in r["runs"][:4]])
    for L, b in r["best"].items():
        print("  best", L, b["start"], b["end"], "busy", b["busy_min"], "events", [(e["t"][:40], e["q"]) for e in b["events"]][:4])
