#!/usr/bin/env python3
"""Fetch official schedule data for the Free Time Vacation planner (session 7d4f79aa).

Runs inside GitHub Actions (the Arena sandbox cannot reach these hosts). Every
source is fetched from the league / team / network that publishes it. Output is
written to planner/data/raw/ and committed back to the branch by the workflow.
Nothing here invents values: if a source fails, the failure is logged in
fetch_log.json and the planner shows that data as missing / unverified.
"""
import gzip
import html
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

OUT = os.path.join(os.path.dirname(__file__), "..", "planner", "data", "raw")
os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (X11; Linux x86_64) FreeTimeVacationPlanner/1.0 (+https://github.com/kanlerxz87-cyber/Freetime2)"
LOG = []


def get(url, timeout=60, extra=None):
    hdr = {"User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip"}
    hdr.update(extra or {})
    req = urllib.request.Request(url, headers=hdr)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            data = gzip.decompress(data)
        return r.status, data


def log(name, url, ok, note=""):
    LOG.append({"name": name, "url": url, "ok": ok, "note": note,
                "fetched_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
    print(("OK  " if ok else "ERR ") + name + " " + note, flush=True)


def save_json(fname, obj):
    with open(os.path.join(OUT, fname), "w") as f:
        json.dump(obj, f, separators=(",", ":"), sort_keys=False)


def to_text(raw):
    s = raw.decode("utf-8", "replace")
    s = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>|</(p|div|li|tr|h[1-6]|td|th|section|article)>", "\n", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


# ---------------------------------------------------------------- MLB (official MLB Stats API)
MLB_FIELDS = ("dates,date,games,gamePk,gameType,gameDate,officialDate,status,detailedState,startTimeTBD,"
              "dayNight,description,doubleHeader,gameNumber,seriesDescription,teams,away,home,team,id,name,"
              "venue,timeZone,tz,broadcasts,type,callSign,homeAway,language,isNational")


def mlb_schedule(start, end):
    url = ("https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=%s&endDate=%s"
           "&gameType=S,E,R,F,D,L,W,A&hydrate=broadcasts(all),venue(timezone)&fields=%s" % (start, end, MLB_FIELDS))
    st, data = get(url, timeout=120)
    j = json.loads(data)
    games = []
    for d in j.get("dates", []):
        for g in d.get("games", []):
            v = g.get("venue", {}) or {}
            tz = (v.get("timeZone") or {}).get("id")
            radio = []
            for b in g.get("broadcasts", []) or []:
                if b.get("type") in ("AM", "FM"):
                    radio.append({"name": b.get("name"), "callSign": b.get("callSign"), "type": b.get("type"),
                                  "homeAway": b.get("homeAway"), "language": b.get("language"),
                                  "isNational": b.get("isNational")})
            games.append({
                "pk": g.get("gamePk"), "type": g.get("gameType"), "utc": g.get("gameDate"),
                "date": g.get("officialDate") or d.get("date"),
                "tbd": bool((g.get("status") or {}).get("startTimeTBD")),
                "state": (g.get("status") or {}).get("detailedState"),
                "dn": g.get("dayNight"), "dh": g.get("doubleHeader"), "gn": g.get("gameNumber"),
                "desc": g.get("description"), "series": g.get("seriesDescription"),
                "away": ((g.get("teams") or {}).get("away") or {}).get("team", {}).get("id"),
                "awayName": ((g.get("teams") or {}).get("away") or {}).get("team", {}).get("name"),
                "home": ((g.get("teams") or {}).get("home") or {}).get("team", {}).get("id"),
                "homeName": ((g.get("teams") or {}).get("home") or {}).get("team", {}).get("name"),
                "venue": v.get("name"), "venueTz": tz, "radio": radio,
            })
    return url, games


def fetch_mlb():
    ranges = [("2026-11-25", "2026-12-31"), ("2027-01-01", "2027-12-31"),
              ("2028-01-01", "2028-12-31"), ("2029-01-01", "2029-12-31")]
    allg, urls = [], []
    for a, b in ranges:
        try:
            url, g = mlb_schedule(a, b)
            urls.append(url)
            allg.extend(g)
            log("mlb_schedule_%s_%s" % (a, b), url, True, "%d games" % len(g))
        except Exception as e:  # noqa: BLE001
            log("mlb_schedule_%s_%s" % (a, b), "statsapi.mlb.com", False, repr(e)[:200])
        time.sleep(1)
    save_json("mlb_games.json", {"source": "https://statsapi.mlb.com/api/v1/schedule", "urls": urls, "games": allg})
    try:
        url = "https://statsapi.mlb.com/api/v1/teams?sportId=1&fields=teams,id,name,abbreviation,teamName,locationName,league,division,venue"
        st, data = get(url)
        save_json("mlb_teams.json", {"source": url, "teams": json.loads(data).get("teams", [])})
        log("mlb_teams", url, True)
    except Exception as e:  # noqa: BLE001
        log("mlb_teams", "statsapi.mlb.com", False, repr(e)[:200])
    # 2026 official time of game (gameDurationMinutes) for the duration model
    for label, gtypes in (("regular", "R"), ("postseason", "F,D,L,W")):
        url = ("https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2026&gameType=%s&hydrate=gameInfo,linescore"
               "&fields=dates,games,gamePk,gameType,status,detailedState,gameInfo,gameDurationMinutes,linescore,currentInning,scheduledInnings" % gtypes)
        try:
            st, data = get(url, timeout=120)
            j = json.loads(data)
            rows = []
            for d in j.get("dates", []):
                for g in d.get("games", []):
                    gi = g.get("gameInfo") or {}
                    ls = g.get("linescore") or {}
                    if gi.get("gameDurationMinutes"):
                        rows.append([g.get("gamePk"), gi.get("gameDurationMinutes"), ls.get("currentInning"), g.get("gameType")])
            nine = [r[1] for r in rows if r[2] == 9]
            out = {"source": url, "games_with_duration": len(rows),
                   "mean_all": round(sum(r[1] for r in rows) / len(rows), 1) if rows else None,
                   "mean_nine_inning": round(sum(nine) / len(nine), 1) if nine else None,
                   "nine_inning_games": len(nine)}
            save_json("mlb_duration_2026_%s.json" % label, out)
            log("mlb_duration_2026_%s" % label, url, bool(rows), json.dumps(out)[:200])
        except Exception as e:  # noqa: BLE001
            log("mlb_duration_2026_%s" % label, url, False, repr(e)[:200])


# ---------------------------------------------------------------- NBA (official NBA CDN) – Warriors
NBA_HDR = {"Origin": "https://www.nba.com", "Referer": "https://www.nba.com/",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}


def fetch_nba():
    url, data = None, None
    for cand in ("https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json",
                 "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2_1.json"):
        try:
            st, data = get(cand, timeout=120, extra=NBA_HDR)
            url = cand
            break
        except Exception as e:  # noqa: BLE001
            log("nba_attempt", cand, False, repr(e)[:200])
    if data is None:
        return
    try:
        j = json.loads(data)
        ls = j.get("leagueSchedule", {})
        out = []
        for gd in ls.get("gameDates", []):
            for g in gd.get("games", []):
                h, a = g.get("homeTeam", {}), g.get("awayTeam", {})
                if "GSW" not in (h.get("teamTricode"), a.get("teamTricode")):
                    continue
                br = g.get("broadcasters", {}) or {}

                def names(k):
                    return [x.get("broadcasterDisplay") for x in (br.get(k) or [])]
                out.append({"gameId": g.get("gameId"), "utc": g.get("gameDateTimeUTC"),
                            "est": g.get("gameDateTimeEst"), "label": g.get("gameLabel"),
                            "status": g.get("gameStatusText"), "home": h.get("teamTricode"),
                            "away": a.get("teamTricode"), "arena": g.get("arenaName"),
                            "city": g.get("arenaCity"), "homeRadio": names("homeRadioBroadcasters"),
                            "awayRadio": names("awayRadioBroadcasters"),
                            "nationalRadio": names("nationalRadioBroadcasters"),
                            "nationalTv": names("nationalTvBroadcasters")})
        save_json("nba_warriors.json", {"source": url, "season": ls.get("seasonYear"), "games": out})
        log("nba_warriors", url, True, "%d GSW games, season %s" % (len(out), ls.get("seasonYear")))
    except Exception as e:  # noqa: BLE001
        log("nba_warriors", url, False, repr(e)[:200])


# ---------------------------------------------------------------- NHL (official NHL API) – Sharks
def fetch_nhl():
    url = "https://api-web.nhle.com/v1/club-schedule-season/SJS/20262027"
    try:
        st, data = get(url)
        j = json.loads(data)
        out = []
        for g in j.get("games", []):
            out.append({"id": g.get("id"), "utc": g.get("startTimeUTC"), "type": g.get("gameType"),
                        "home": (g.get("homeTeam") or {}).get("abbrev"), "away": (g.get("awayTeam") or {}).get("abbrev"),
                        "venue": ((g.get("venue") or {}).get("default")), "state": g.get("gameState")})
        save_json("nhl_sharks.json", {"source": url, "games": out})
        log("nhl_sharks", url, True, "%d games" % len(out))
    except Exception as e:  # noqa: BLE001
        log("nhl_sharks", url, False, repr(e)[:200])


# ---------------------------------------------------------------- HTML pages saved as text for line-by-line checks
PAGES = {
    "nfl_important_dates": "https://www.nfl.com/news/2026-27-national-football-league-important-dates",
    "nfl_reg12": "https://www.nfl.com/schedules/2026/REG12/",
    "nfl_reg13": "https://www.nfl.com/schedules/2026/REG13/",
    "nfl_reg14": "https://www.nfl.com/schedules/2026/REG14/",
    "nfl_reg15": "https://www.nfl.com/schedules/2026/REG15/",
    "nfl_reg16": "https://www.nfl.com/schedules/2026/REG16/",
    "nfl_reg17": "https://www.nfl.com/schedules/2026/REG17/",
    "nfl_reg18": "https://www.nfl.com/schedules/2026/REG18/",
    "nfl_post1": "https://www.nfl.com/schedules/2026/POST1/",
    "nfl_post2": "https://www.nfl.com/schedules/2026/POST2/",
    "nfl_post3": "https://www.nfl.com/schedules/2026/POST3/",
    "nfl_post4": "https://www.nfl.com/schedules/2026/POST4/",
    "niners_schedule": "https://www.49ers.com/schedule/",
    "w1_nfl": "https://www.westwoodonesports.com/nfl-schedule/",
    "w1_grid_nfl": "https://www.westwoodonesports.com/more/eventGrid?id=47029&range=current&offset=0&limit=60&timezone=America/Los_Angeles&widgetTitle=NFL",
    "w1_grid_ncaaf": "https://www.westwoodonesports.com/more/eventGrid?id=47030&range=current&offset=0&limit=60&timezone=America/Los_Angeles&widgetTitle=NCAAF",
    "w1_grid_ncaab": "https://www.westwoodonesports.com/more/eventGrid?id=47031&range=current&offset=0&limit=60&timezone=America/Los_Angeles&widgetTitle=NCAAB",
    "stanford_fb": "https://gostanford.com/sports/football/schedule",
    "cal_fb_text": "https://calbears.com/sports/football/schedule/text",
    "athletics_affiliates": "https://www.mlb.com/athletics/schedule/affiliates",
    "giants_broadcast": "https://www.mlb.com/giants/schedule/broadcast",
    "quakes_2027": "https://www.sjearthquakes.com/news/san-jose-earthquakes-announce-2027-major-league-soccer-sprint-season-schedule-presented-by-habbas-law",
    "mlb_2027_spring": "https://www.mlb.com/press-release/press-release-mlb-announces-2027-spring-training-schedule",
    "giants_2027_release": "https://www.mlb.com/press-release/press-release-giants-announce-tentative-2027-regular-season-schedule",
    "nfl_pro_bowl_change": "https://www.nfl.com/news/nfl-elevates-pro-bowl-selection-game-s-will-cease-being-contested",
    "sb_lxii": "https://www.mercedesbenzstadium.com/events/super-bowl-lxii",
    "sb_lxiii": "https://www.allegiantstadium.com/events/detail/super-bowl-lxiii",
    "cfp_future": "https://collegefootballplayoff.com/sports/2018/8/31/cfp-games-schedule",
    "mlb_avg_time_2025": "https://www.mlb.com/news/mlb-average-game-time-under-three-hours-third-straight-year",
    "warriors_broadcast_2026_27": "https://www.nba.com/warriors/news/warriors-announce-2026-27-television-radio-broadcast-schedules-20260824",
    "earthquakes_radio_2026": "https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season",
    "stanford_radio_2026": "https://gostanford.com/news/2026/07/30/2026-football-radio-broadcast-team-announced",
    "cal_mbb": "https://calbears.com/sports/mens-basketball/schedule/text",
}


def fetch_pages():
    os.makedirs(os.path.join(OUT, "pages"), exist_ok=True)
    for name, url in PAGES.items():
        try:
            st, data = get(url)
            txt = to_text(data)
            with open(os.path.join(OUT, "pages", name + ".txt"), "w") as f:
                f.write("SOURCE: %s\nFETCHED_UTC: %s\n\n" % (url, datetime.now(timezone.utc).isoformat()))
                f.write(txt[:400000])
            log("page_" + name, url, True, "%d chars text" % len(txt))
        except Exception as e:  # noqa: BLE001
            log("page_" + name, url, False, repr(e)[:200])
        time.sleep(0.5)


if __name__ == "__main__":
    fetch_mlb()
    fetch_nba()
    fetch_nhl()
    fetch_pages()
    save_json("fetch_log.json", {"run_utc": datetime.now(timezone.utc).isoformat(), "entries": LOG})
    print("done", sum(1 for x in LOG if x["ok"]), "ok of", len(LOG))
    sys.exit(0)
