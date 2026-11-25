(async () => {
  FTV.renderChrome("scoreboard");

  const MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
  ];
  const DOWS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const MIN_DATE = "2026-11-25";
  const MAX_DATE = "2029-12-31";

  const [dailyData, eventsData] = await Promise.all([
    FTV.loadJSON("data/daily_summary.json"),
    FTV.loadJSON("data/all_events.json"),
  ]);

  const dailyMap = new Map();
  for (const d of dailyData.days) dailyMap.set(d.date, d);

  const eventsByDate = new Map();
  for (const e of eventsData.events) {
    if (!eventsByDate.has(e.date)) eventsByDate.set(e.date, []);
    eventsByDate.get(e.date).push(e);
  }

  // Populate month dropdown
  const monthSel = document.getElementById("cal-month-select");
  monthSel.innerHTML = MONTHS.map((m, i) => `<option value="${i + 1}">${m}</option>`).join("");

  const yearSel = document.getElementById("cal-year-select");
  const datePicker = document.getElementById("date-picker");
  const filterModeSel = document.getElementById("filter-mode");
  const bufferChk = document.getElementById("chk-buffer");

  // Parse ?date=YYYY-MM-DD from URL if present
  const params = new URLSearchParams(window.location.search);
  let selectedDate = params.get("date") || FTV.TODAY_REF;
  if (!dailyMap.has(selectedDate)) selectedDate = FTV.TODAY_REF;

  let viewYear = Number(selectedDate.slice(0, 4));
  let viewMonth = Number(selectedDate.slice(5, 7));

  function shiftDate(iso, deltaDays) {
    const [y, m, d] = iso.split("-").map(Number);
    const dt = new Date(Date.UTC(y, m - 1, d + deltaDays));
    const next = dt.toISOString().slice(0, 10);
    if (next < MIN_DATE) return MIN_DATE;
    if (next > MAX_DATE) return MAX_DATE;
    return next;
  }

  function filterEventsForDay(evs, mode) {
    if (mode === "noSpring") {
      return evs.filter(
        (e) =>
          !e.phase.includes("Spring Training") &&
          !e.phase.includes("Exhibition") &&
          !e.phase.includes("Preseason")
      );
    }
    if (mode === "highPriority") {
      return evs.filter((e) => e.highPriority);
    }
    return evs;
  }

  function isDayFree(dayRec, mode) {
    if (mode === "noSpring") return dayRec.freeNoSpringPre;
    if (mode === "highPriority") return dayRec.freeHighPriority;
    return dayRec.freeStrict;
  }

  function renderCalendar() {
    monthSel.value = String(viewMonth);
    yearSel.value = String(viewYear);

    const firstDay = new Date(Date.UTC(viewYear, viewMonth - 1, 1));
    const startDow = firstDay.getUTCDay();
    const daysInMonth = new Date(Date.UTC(viewYear, viewMonth, 0)).getUTCDate();
    const mode = filterModeSel.value;

    let html = DOWS.map((d) => `<div class="cal-dow">${d}</div>`).join("");
    for (let i = 0; i < startDow; i++) {
      html += `<div class="cal-cell empty"></div>`;
    }
    for (let day = 1; day <= daysInMonth; day++) {
      const iso = `${viewYear}-${String(viewMonth).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
      const rec = dailyMap.get(iso);
      if (!rec) {
        html += `<div class="cal-cell" style="opacity:0.3;cursor:default;"><span class="cal-day-num">${day}</span><span class="cal-day-tag">—</span></div>`;
        continue;
      }
      const free = isDayFree(rec, mode);
      let cls = "cal-cell";
      let tag = "";
      if (free) {
        cls += " free";
        tag = "FREE";
      } else if (rec.highPriorityCount > 0) {
        cls += " busy-hp";
        tag = `${rec.highPriorityCount} HP`;
      } else {
        cls += " busy-std";
        tag = `${rec.eventCount} gm`;
      }
      if (iso === selectedDate) cls += " selected";

      html += `
        <div class="${cls}" data-iso="${iso}" role="button" tabindex="0" aria-label="${iso} ${tag}">
          <span class="cal-day-num">${day}</span>
          <span class="cal-day-tag">${tag}</span>
        </div>
      `;
    }

    const grid = document.getElementById("cal-grid");
    grid.innerHTML = html;
    grid.querySelectorAll(".cal-cell[data-iso]").forEach((el) => {
      el.addEventListener("click", () => selectDate(el.dataset.iso));
    });
  }

  function renderDayDetail() {
    const rec = dailyMap.get(selectedDate);
    const mode = filterModeSel.value;
    const useBuffer = bufferChk.checked;
    const buf = useBuffer ? 30 : 0;

    const allDayEvents = eventsByDate.get(selectedDate) || [];
    const activeEvents = filterEventsForDay(allDayEvents, mode);

    const busyAll = FTV.mergeIntervals(
      activeEvents.map((e) => [e.startMinPST - buf, e.startMinPST + e.durationMin + buf])
    );
    const busyHP = FTV.mergeIntervals(
      activeEvents.filter((e) => e.highPriority).map((e) => [e.startMinPST - buf, e.startMinPST + e.durationMin + buf])
    );
    const freeInts = FTV.complementIntervals(busyAll);
    const busyMins = busyAll.reduce((acc, [s, e]) => acc + (e - s), 0);
    const freeMins = 1440 - busyMins;

    const dstNote = rec.isDST
      ? `<span class="badge badge-est" title="California observes PDT (UTC-7) on this date; all times shown remain fixed in PST (UTC-8) per specification">DST Active in CA (Local PDT = PST + 1 hr)</span>`
      : `<span class="badge badge-verified">Standard Time (PST = Local SF Time)</span>`;

    const estBanner = activeEvents.some((e) => e.status === "ESTIMATED")
      ? `<div class="callout amber small" style="margin-top:10px;"><strong>Estimated / Unreleased Schedule Notice:</strong> One or more events on this date are modeled estimates for an unreleased future schedule. Official fields remain blank until confirmed.</div>`
      : activeEvents.some((e) => e.startTimeTBD)
      ? `<div class="callout small" style="margin-top:10px;"><strong>Official Date · Start Time TBD Notice:</strong> Official dates are confirmed, while TBD start times use ballpark-standard PST estimates for free-time modeling.</div>`
      : "";

    const statusPill =
      activeEvents.length === 0
        ? `<span class="badge badge-free" style="font-size:0.85rem;padding:5px 12px;">100% FREE — ZERO TRACKED GAMES ON AIR</span>`
        : `<span class="badge badge-busy" style="font-size:0.85rem;padding:5px 12px;">${activeEvents.length} ACTIVE ITEM(S) · ${FTV.fmtDuration(busyMins)} ON AIR</span>`;

    document.getElementById("day-header-panel").innerHTML = `
      <div class="card-header">
        <div>
          <h2 style="font-size:1.35rem;">${FTV.fmtDateNice(selectedDate)}</h2>
          <div class="mt-1" style="display:flex;flex-wrap:wrap;gap:6px;">
            ${statusPill}
            ${dstNote}
            ${useBuffer ? `<span class="badge badge-ww1">+30m Pre/Post Buffer ON</span>` : ""}
          </div>
        </div>
        <div style="text-align:right;">
          <div class="kpi-label">Free Time Today (PST)</div>
          <div class="kpi-value text-green" style="margin:2px 0;">${FTV.fmtDuration(freeMins)}</div>
          <div class="small text-muted">Busy: ${FTV.fmtDuration(busyMins)} · MLB League Games: ${rec.mlbGamesCount}</div>
        </div>
      </div>

      ${FTV.renderTimeline(busyAll, busyHP)}

      <div>
        <strong class="small">Exact Free-Time Windows (PST, UTC-8):</strong>
        <div class="window-chips">
          ${freeInts
            .map(
              ([s, e]) =>
                `<span class="window-chip">${FTV.fmtMin(s)} – ${FTV.fmtMin(e)} PST (${FTV.fmtDuration(e - s)})</span>`
            )
            .join("")}
        </div>
      </div>

      ${
        busyAll.length
          ? `<div class="mt-2 small text-muted"><strong>Blocked Sports Windows (PST):</strong> ${busyAll
              .map(([s, e]) => `${FTV.fmtMin(s)} – ${FTV.fmtMin(e)} PST`)
              .join(" &nbsp;|&nbsp; ")}</div>`
          : ""
      }
      ${estBanner}
    `;

    // Games list
    document.getElementById("games-heading").textContent = `Scoreboard Slate — ${FTV.fmtDateNice(selectedDate)}`;
    document.getElementById("games-sub").textContent =
      mode === "strict"
        ? `Showing all ${activeEvents.length} tracked item(s)`
        : `Filtered (${activeEvents.length} of ${allDayEvents.length} total item(s) on this date)`;

    if (!activeEvents.length) {
      document.getElementById("games-list").innerHTML = `
        <div class="callout green">
          <strong>ZERO TRACKED SPORTS BROADCASTS SCHEDULED!</strong><br/>
          All 24 hours (${FTV.fmtMin(0)} – ${FTV.fmtMin(1440)} PST) are completely clear under your active filter mode.
          ${
            allDayEvents.length > 0
              ? `<br/><span class="small text-muted">Note: ${allDayEvents.length} lower-priority or Spring Training/Preseason item(s) exist on this date under Strict mode.</span>`
              : ""
          }
        </div>
      `;
    } else {
      document.getElementById("games-list").innerHTML = activeEvents
        .map((e) => {
          const endMin = Math.min(1440, e.startMinPST + e.durationMin);
          const timeRange = `${FTV.fmtMin(e.startMinPST)} – ${FTV.fmtMin(endMin)} PST`;
          return `
            <div class="game-card ${e.highPriority ? "hp" : ""}">
              <div class="game-card-top">
                <div style="display:flex;flex-wrap:wrap;gap:5px;">
                  <span class="badge badge-league">${FTV.esc(e.league)} · ${FTV.esc(e.phase)}</span>
                  ${e.highPriority ? `<span class="badge badge-hp">HIGH PRIORITY</span>` : ""}
                  ${e.isWestwoodOne ? `<span class="badge badge-ww1">WESTWOOD ONE</span>` : ""}
                  ${FTV.statusBadge(e.status)}
                </div>
                <div class="small" style="text-align:right;">
                  <div><strong>Official PST:</strong> ${e.officialTimePST ? FTV.esc(e.officialTimePST) : `<span class="text-amber">Blank (TBD/Est.)</span>`}</div>
                  ${e.estimatedTimePST ? `<div class="text-amber">Est. Start: ${FTV.esc(e.estimatedTimePST)}</div>` : ""}
                </div>
              </div>
              <div class="game-title">${FTV.esc(e.title)}</div>
              <div class="game-meta">
                <span><strong>Window (PST):</strong> ${timeRange} (Avg ${FTV.fmtDuration(e.durationMin)}${e.halftimeMin ? `, incl. ${e.halftimeMin}m halftime` : ""})</span>
                <span><strong>Venue:</strong> ${FTV.esc(e.venue)}</span>
              </div>
              <div class="game-meta">
                <span><strong>SF 94122 Radio:</strong> ${FTV.esc(e.radioStations)}</span>
                <span><a href="${FTV.esc(e.sourceUrl)}" target="_blank" rel="noopener"><strong>Official Source: ${FTV.esc(e.sourceLabel)} &nearr;</strong></a></span>
              </div>
              ${e.notes ? `<div class="small text-muted mt-1">${FTV.esc(e.notes)}</div>` : ""}
            </div>
          `;
        })
        .join("");
    }
  }

  function selectDate(iso) {
    if (!dailyMap.has(iso)) return;
    selectedDate = iso;
    datePicker.value = iso;
    viewYear = Number(iso.slice(0, 4));
    viewMonth = Number(iso.slice(5, 7));
    const url = new URL(window.location.href);
    url.searchParams.set("date", iso);
    window.history.replaceState({}, "", url);
    renderCalendar();
    renderDayDetail();
  }

  // Event listeners
  document.getElementById("btn-prev").addEventListener("click", () => selectDate(shiftDate(selectedDate, -1)));
  document.getElementById("btn-today").addEventListener("click", () => selectDate(FTV.TODAY_REF));
  document.getElementById("btn-next").addEventListener("click", () => selectDate(shiftDate(selectedDate, 1)));
  datePicker.addEventListener("change", (ev) => {
    if (dailyMap.has(ev.target.value)) selectDate(ev.target.value);
  });
  filterModeSel.addEventListener("change", () => {
    renderCalendar();
    renderDayDetail();
  });
  bufferChk.addEventListener("change", renderDayDetail);

  monthSel.addEventListener("change", () => {
    viewMonth = Number(monthSel.value);
    renderCalendar();
  });
  yearSel.addEventListener("change", () => {
    viewYear = Number(yearSel.value);
    renderCalendar();
  });
  document.getElementById("cal-prev-month").addEventListener("click", () => {
    viewMonth -= 1;
    if (viewMonth < 1) {
      viewMonth = 12;
      viewYear = Math.max(2026, viewYear - 1);
    }
    renderCalendar();
  });
  document.getElementById("cal-next-month").addEventListener("click", () => {
    viewMonth += 1;
    if (viewMonth > 12) {
      viewMonth = 1;
      viewYear = Math.min(2029, viewYear + 1);
    }
    renderCalendar();
  });

  document.querySelectorAll(".jump-btn").forEach((btn) => {
    btn.addEventListener("click", () => selectDate(btn.dataset.date));
  });

  // Initial render
  selectDate(selectedDate);
})();
