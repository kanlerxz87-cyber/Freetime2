(function () {
  const F = window.FT;
  const $ = (id) => document.getElementById(id);
  let DATA = null;
  let current = null;

  function todayPT() {
    return F.ptParts(new Date()).date;
  }

  function scopeFn() {
    return $("scope").value === "sf" ? F.scopeSF : F.scopeAll;
  }

  function pctLeft(min) { return (min / 1440) * 100; }

  function setHash(d) {
    history.replaceState(null, "", "#" + d);
  }

  function renderDay(dateStr) {
    current = dateStr;
    setHash(dateStr);
    $("pick").value = dateStr;
    const cov = F.coverageFor(dateStr, DATA.snap, DATA.mlb);
    const model = F.dayModel(dateStr, DATA.events, scopeFn());
    const st = F.dayStatus(model, cov);

    $("dayCard").hidden = false;
    $("dayTitle").textContent = F.fmtDayLong(dateStr);
    const pillCls = { busy: "b-busy", cand: "b-cand", unk: "b-unk" }[st.key];
    $("dayPill").innerHTML = '<span class="badge ' + pillCls + '" style="font-size:14px;padding:6px 12px">' + F.esc(st.label) + "</span>";

    const coverageTxt = "Coverage — MLB: " + (cov.MLB === "live" ? "live official feed" : "not loaded") +
      " · NFL: " + (cov.NFL === "partial" ? "partial (national radio + 49ers only)" : "not loaded") +
      " · NCAAF: " + (cov.NCAAF === "partial" ? "partial (Stanford & Cal only)" : "not loaded");
    $("dayNote").textContent = coverageTxt;

    // timeline
    const tl = $("timeline");
    tl.innerHTML = "";
    for (const [s, e, ev] of model.busy) {
      const seg = document.createElement("div");
      seg.className = "seg";
      seg.style.left = pctLeft(s) + "%";
      seg.style.width = pctLeft(e - s) + "%";
      seg.title = F.fmtClock(s) + " – " + F.fmtClock(e) + " · " + ev.title;
      tl.appendChild(seg);
    }

    // free table
    const ft = $("freeTable").querySelector("tbody");
    if (!model.free.length) {
      ft.innerHTML = '<tr><td colspan="4">No free time: games fill the day under the chosen scope.</td></tr>';
    } else {
      ft.innerHTML = model.free.map(([s, e]) => {
        const len = e - s;
        const note = len >= 1440 ? "Whole day free in loaded data" : (s === 0 ? "Before first game" : (e === 1440 ? "After last game" : "Between games"));
        return "<tr><td>" + F.fmtClock(s) + "</td><td>" + F.fmtClock(e) + "</td><td>" + F.fmtDur(len) + "</td><td>" + F.esc(note) + "</td></tr>";
      }).join("");
    }

    // game table
    const gt = $("gameTable").querySelector("tbody");
    if (!model.list.length) {
      gt.innerHTML = '<tr><td colspan="7">No games listed for this day under the chosen scope.' +
        (st.key === "cand" ? " MLB feed is loaded, but NFL/NCAAF schedules for this date are not fully loaded, so this is NOT a verified free day." : "") + "</td></tr>";
    } else {
      gt.innerHTML = model.list.map((e) => {
        const busyUntil = F.fmtClock(Math.min(1440, e.ptMin + e.durMin)) + (e.ptMin + e.durMin > 1440 ? " (next day)" : "");
        const pr = e.priority === "HIGH" ? F.badge("high", "High") : F.badge("unverified", "Standard");
        const timeCell = F.fmtClock(e.ptMin) + (e.status === "estimate" ? " <em>(est.)</em>" : "");
        const note = [e.timeNote, e.result ? "Result: " + e.result : "", e.flag ? "See " + e.flag : ""].filter(Boolean).join(" · ");
        return "<tr class=\"" + (e.priority === "HIGH" ? "hi" : "") + "\"><td>" + timeCell + "</td><td>" + busyUntil + "</td><td>" + F.esc(e.category) + "</td><td><b>" +
          F.esc(e.title) + "</b>" + (e.network ? '<div class="note">' + F.esc(e.network) + "</div>" : "") +
          (note ? '<div class="note">' + F.esc(note) + "</div>" : "") + "</td><td>" + pr + "</td><td>" + F.statusBadge(e.status) +
          "</td><td><a href=\"" + F.esc(e.source_url) + "\" target=\"_blank\" rel=\"noopener\">" + F.esc(e.source_name) + "</a></td></tr>";
      }).join("");
    }
    $("durNote").textContent = "Busy-until times use the average length for each category: MLB 2:38 (official MLB 2025 average), NFL 3:03 and college 3:27 (third-party averages — see Research). Start times marked (est.) are estimates.";

    renderStrip(dateStr);
  }

  function renderStrip(dateStr) {
    const wrap = $("strip");
    let html = "";
    for (let i = 0; i < 7; i++) {
      const d = F.addDays(dateStr, i);
      const cov = F.coverageFor(d, DATA.snap, DATA.mlb);
      const model = F.dayModel(d, DATA.events, scopeFn());
      const st = F.dayStatus(model, cov);
      const dotCls = { busy: "dot-busy", cand: "dot-cand", unk: "dot-unk" }[st.key];
      const freeTxt = model.list.length ? model.list.length + " game" + (model.list.length > 1 ? "s" : "") : "no game listed";
      html += '<a href="#' + d + '" data-d="' + d + '" class="' + (d === dateStr ? "sel" : "") + '">' +
        "<div><b>" + F.fmtDayShort(d) + "</b></div><div>" + F.esc(freeTxt) + '</div><span class="dot ' + dotCls + '"></span></a>';
    }
    wrap.innerHTML = html;
    wrap.querySelectorAll("a").forEach((a) => a.addEventListener("click", (ev) => { ev.preventDefault(); renderDay(a.dataset.d); }));
  }

  function bindControls() {
    $("prev").onclick = () => renderDay(F.addDays(current, -1));
    $("next").onclick = () => renderDay(F.addDays(current, 1));
    $("today").onclick = () => renderDay(todayPT());
    $("pick").onchange = (e) => e.target.value && renderDay(e.target.value);
    $("scope").onchange = () => renderDay(current);
    window.addEventListener("hashchange", () => {
      const h = location.hash.slice(1);
      if (/^\d{4}-\d{2}-\d{2}$/.test(h) && h !== current) renderDay(h);
    });
  }

  async function init() {
    try {
      DATA = await F.loadAll();
      const st = $("status");
      const errs = DATA.mlb.errors;
      if (errs.length) {
        st.className = "warn";
        st.innerHTML = "MLB live feed did not load in this browser (" + F.esc(errs.join("; ")) + "). MLB days are shown as UNKNOWN. Open <a href=\"https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2027\" target=\"_blank\" rel=\"noopener\">the MLB Stats API 2027 feed</a> to check the games directly. See Flagged for Review.";
      } else {
        st.className = "ok";
        st.innerHTML = "Loaded official data: MLB Stats API seasons " + DATA.mlb.loaded.join(", ") + " (" + DATA.mlb.events.length.toLocaleString() + " MLB games) + " + DATA.snap.events.length + " hand-verified rows from team and league pages. Verified on " + DATA.snap.meta.verified_on + ".";
      }
      bindControls();
      const h = location.hash.slice(1);
      renderDay(/^\d{4}-\d{2}-\d{2}$/.test(h) ? h : todayPT());
    } catch (err) {
      $("status").className = "warn";
      $("status").textContent = "Could not load the schedule data: " + err.message;
    }
  }
  init();
})();
