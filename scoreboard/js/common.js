/* Shared helpers: data loading, Pacific-time math, status badges, tables.
   Every value shown on the site comes from docs/data/*.json or from the MLB Stats API. */
(function () {
  const MLB_API = "https://statsapi.mlb.com/api/v1";
  const HIGH_MLB_IDS = [137, 133]; // San Francisco Giants, Athletics
  const MLB_FIELDS = "dates,date,games,gamePk,gameDate,gameType,status,startTimeTBD,teams,away,home,team,id,name";

  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  async function getJSON(url) {
    const r = await fetch(url, { cache: "no-store" });
    if (!r.ok) throw new Error(url + " → HTTP " + r.status);
    return r.json();
  }

  // Pacific wall-clock date ('YYYY-MM-DD') and minutes after midnight for an instant.
  const ptFmt = new Intl.DateTimeFormat("en-CA", { timeZone: "America/Los_Angeles", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hourCycle: "h23" });
  function ptParts(instant) {
    const p = {};
    for (const x of ptFmt.formatToParts(instant)) p[x.type] = x.value;
    return { date: p.year + "-" + p.month + "-" + p.day, min: (+p.hour) * 60 + (+p.minute) };
  }

  function addDays(dateStr, n) {
    const d = new Date(dateStr + "T12:00:00Z");
    d.setUTCDate(d.getUTCDate() + n);
    return d.toISOString().slice(0, 10);
  }
  function fmtDayLong(dateStr) {
    return new Date(dateStr + "T12:00:00Z").toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric", timeZone: "UTC" });
  }
  function fmtDayShort(dateStr) {
    return new Date(dateStr + "T12:00:00Z").toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", timeZone: "UTC" });
  }
  function fmtClock(min) {
    const m = ((Math.round(min) % 1440) + 1440) % 1440;
    const h24 = Math.floor(m / 60), mm = m % 60;
    const h12 = h24 % 12 === 0 ? 12 : h24 % 12;
    return h12 + ":" + String(mm).padStart(2, "0") + " " + (h24 < 12 ? "AM" : "PM");
  }
  function fmtClockHHMM(hhmm) {
    const [h, m] = hhmm.split(":").map(Number);
    return fmtClock(h * 60 + m);
  }
  function fmtDur(min) {
    const h = Math.floor(min / 60), m = min % 60;
    return (h ? h + " h " : "") + m + " min";
  }

  function badge(kind, label) {
    const cls = { verified: "b-verified", conflict: "b-conflict", estimate: "b-estimate", unverified: "b-unverified", high: "b-high", free: "b-free", busy: "b-busy", cand: "b-cand", unk: "b-unk" }[kind] || "b-unverified";
    return '<span class="badge ' + cls + '">' + esc(label) + "</span>";
  }
  function statusBadge(s) {
    if (s === "verified") return badge("verified", "Verified");
    if (s === "conflict") return badge("conflict", "Time conflict");
    if (s === "estimate") return badge("estimate", "Estimate");
    return badge("unverified", "Unverified");
  }

  // Snapshot-only category events -> normalized event objects.
  function snapshotEvents(snap) {
    const dur = snap.durations_minutes, tbd = snap.tbd_start_estimate_pt;
    const out = [];
    for (const e of snap.events) {
      if (e.dup_of) continue; // same game already listed from Westwood One (kept on NFL page; not double-counted on the calendar)
      if (!e.date) continue; // dateless rows (e.g. Week 18 at ARI) are listed on the pages but never placed on the calendar
      let ptMin, status = e.status, timeNote = "";
      if (e.time_pt) {
        const [h, m] = e.time_pt.split(":").map(Number);
        ptMin = h * 60 + m;
      } else {
        const [h, m] = tbd[e.category].time_pt.split(":").map(Number);
        ptMin = h * 60 + m;
        status = "estimate";
        timeNote = "Start time not published — ESTIMATE " + fmtClock(ptMin) + " PT";
      }
      out.push({
        id: e.id, category: e.category, date: e.date, ptMin: ptMin, durMin: dur[e.category].minutes,
        title: e.title, priority: e.priority || "STANDARD", status: status, flag: e.flag || null,
        timeNote: timeNote, timePublished: e.time_published || "", network: e.network || "",
        venue: e.venue || "", result: e.result || "", source_url: e.source_url, source_name: e.source_name,
        mlbIds: []
      });
    }
    return out;
  }

  // Live MLB Stats API schedule for the given seasons (all 30 clubs, all game types).
  async function loadMLB(seasons, estimateMin) {
    const result = { events: [], loaded: [], errors: [] };
    await Promise.all(seasons.map(async (y) => {
      try {
        const j = await getJSON(MLB_API + "/schedule?sportId=1&season=" + y + "&fields=" + MLB_FIELDS);
        if (!(j.dates || []).some((d) => (d.games || []).length)) return; // no games published for this season yet
        result.loaded.push(y);
        for (const d of j.dates || []) {
          for (const g of d.games || []) {
            const away = g.teams.away.team, home = g.teams.home.team;
            const tbd = !!(g.status && g.status.startTimeTBD);
            let date, ptMin, status = "verified", timeNote = "";
            if (tbd) {
              date = d.date; ptMin = estimateMin; status = "estimate";
              timeNote = "MLB start time TBD — ESTIMATE " + fmtClock(ptMin) + " PT";
            } else {
              const p = ptParts(new Date(g.gameDate));
              date = p.date; ptMin = p.min;
            }
            const high = HIGH_MLB_IDS.includes(away.id) || HIGH_MLB_IDS.includes(home.id);
            result.events.push({
              id: "MLB-" + g.gamePk, category: "MLB", date: date, ptMin: ptMin, durMin: 158,
              title: away.name + " at " + home.name, priority: high ? "HIGH" : "STANDARD",
              status: status, flag: tbd ? "F8" : null, timeNote: timeNote,
              timePublished: tbd ? "TBD in MLB feed" : "", network: "", venue: "", result: "",
              source_url: "https://statsapi.mlb.com/api/v1.1/game/" + g.gamePk + "/feed/live",
              source_name: "MLB Stats API", mlbIds: [away.id, home.id], gameType: g.gameType
            });
          }
        }
      } catch (err) {
        result.errors.push(String(err.message || err));
      }
    }));
    result.loaded.sort();
    return result;
  }

  // Merge busy intervals for a PT day and return busy list + free gaps.
  function dayModel(dateStr, events, scopeFn) {
    const prev = addDays(dateStr, -1);
    const list = [], busy = [];
    for (const e of events) {
      if (scopeFn && !scopeFn(e)) continue;
      if (e.date === dateStr) {
        list.push(e);
        busy.push([e.ptMin, Math.min(1440, e.ptMin + e.durMin), e]);
      } else if (e.date === prev) {
        const en = e.ptMin + e.durMin - 1440;
        if (en > 0) busy.push([0, Math.min(1440, en), e]);
      }
    }
    busy.sort((a, b) => a[0] - b[0]);
    const free = [];
    let cursor = 0;
    for (const [s, en] of busy) {
      if (s > cursor) free.push([cursor, s]);
      cursor = Math.max(cursor, en);
    }
    if (cursor < 1440) free.push([cursor, 1440]);
    list.sort((a, b) => a.ptMin - b.ptMin);
    return { list: list, busy: busy, free: free };
  }

  // Coverage of each category for a date. Returns "full" | "partial" | "none" | "live".
  function coverageFor(dateStr, snap, mlb) {
    // A season counts as loaded only if the MLB feed returned at least one game for it.
    // Its feed covers every day of that calendar year (regular season, spring training, postseason).
    const y = Number(dateStr.slice(0, 4));
    const mlbC = mlb.loaded.includes(y) ? "live" : "none";
    const nflP = dateStr >= "2026-11-25" && dateStr <= "2027-01-10";
    const ncaaP = dateStr >= "2026-08-29" && dateStr <= "2026-11-28";
    return { MLB: mlbC, NFL: nflP ? "partial" : "none", NCAAF: ncaaP ? "partial" : "none" };
  }

  // Day status: BUSY (listed games), CANDIDATE FREE (MLB feed clear, NFL/NCAA not fully loaded), UNKNOWN.
  function dayStatus(model, cov) {
    if (model.list.length) return { key: "busy", label: "GAMES ON THIS DAY" };
    if (cov.MLB === "live") return { key: "cand", label: "NO GAMES LISTED — not verified free" };
    return { key: "unk", label: "UNKNOWN — MLB data not loaded for this date" };
  }

  // Shared loader used by every page that needs the calendar data.
  async function loadAll() {
    const snap = await getJSON("data/snapshot.json");
    const teams = await getJSON("data/mlb-teams.json");
    const [eh, em] = snap.tbd_start_estimate_pt.MLB.time_pt.split(":").map(Number);
    const mlb = await loadMLB([2026, 2027, 2028], eh * 60 + em);
    const events = snapshotEvents(snap).concat(mlb.events);
    return { snap: snap, teams: teams, mlb: mlb, events: events };
  }

  function scopeAll() { return null; }
  function scopeSF(e) {
    if (e.category !== "MLB") return true; // all NFL/college rows loaded are SF-relevant (49ers, Stanford, Cal, Westwood One national radio)
    return e.mlbIds.some((id) => HIGH_MLB_IDS.includes(id));
  }

  // Verified SF-relevant filter for snapshot rows: used by index for MLB-only streaks.
  window.FT = {
    MLB_API, HIGH_MLB_IDS, esc, getJSON, ptParts, addDays, fmtDayLong, fmtDayShort, fmtClock, fmtClockHHMM,
    fmtDur, badge, statusBadge, snapshotEvents, loadMLB, dayModel, coverageFor, dayStatus, loadAll, scopeAll, scopeSF
  };
})();
