(async () => {
  FTV.renderChrome("home");

  try {
    const [meta, vac, daily, eventsData] = await Promise.all([
      FTV.loadJSON("data/metadata.json"),
      FTV.loadJSON("data/vacation_windows.json"),
      FTV.loadJSON("data/daily_summary.json"),
      FTV.loadJSON("data/all_events.json"),
    ]);

    // Meta strip
    document.getElementById("meta-strip").innerHTML = `
      <span class="meta-pill">Last Verified: <strong>${FTV.esc(meta.lastVerifiedDate)}</strong></span>
      <span class="meta-pill">Display Timezone: <strong>PST (UTC-8)</strong></span>
      <span class="meta-pill">Days Modeled: <strong>${meta.totalDaysCovered.toLocaleString()}</strong></span>
      <span class="meta-pill">Verified Events: <strong>${meta.verifiedEventsCount.toLocaleString()}</strong></span>
      <span class="meta-pill">Estimated (2027–29 Unreleased): <strong>${meta.estimatedEventsCount.toLocaleString()}</strong></span>
    `;

    // Year summary cards
    const cardsEl = document.getElementById("year-summary-cards");
    const yearNotes = {
      "2027": {
        badge: `<span class="badge badge-verified">MLB &amp; NFL PLAYOFFS VERIFIED</span>`,
        topNoSpring: "Mon, Feb 15 – Tue, Mar 23, 2027",
        topStrict: "Feb 15–18 (4d) · Jan 25–30 (6d) · Feb 1–6 (6d) · Feb 8–13 (6d)",
        lowImpact3W: "Jan 24 – Feb 13 (18 zero-game days / 3 game days) or Feb 1 – Feb 18 (16/18 free!)",
        highlight: "Super Bowl LXI = Feb 14 (Official); MLB Spring = Feb 19 (Official); MLB Opening Night = Mar 24 (Official); MLB All-Star Off Day = Wed Jul 14 (Official).",
      },
      "2028": {
        badge: `<span class="badge badge-est">ESTIMATED · SF ALL-STAR HOST</span>`,
        topNoSpring: "Mon, Feb 14 – Wed, Mar 22, 2028 (Est.)",
        topStrict: "Jan 24–29 (6d) · Jan 31–Feb 5 (6d) · Feb 7–12 (6d) · Feb 14–17 (4d)",
        lowImpact3W: "Jan 23 – Feb 12 (18 zero-game days / 3 game days, Est.)",
        highlight: "Super Bowl LXII in Atlanta (planned Feb 13, 2028). SF Giants officially host 2028 MLB All-Star Game at Oracle Park (July 2028 — LA Olympics coordination TBD!).",
      },
      "2029": {
        badge: `<span class="badge badge-est">ESTIMATED (UNRELEASED)</span>`,
        topNoSpring: "Mon, Feb 12 – Wed, Mar 28, 2029 (Est.)",
        topStrict: "Feb 12–20 (9 consecutive days!) · Jan 22–27 (6d) · Jan 29–Feb 3 (6d)",
        lowImpact3W: "Jan 29 – Feb 18 (19 zero-game days / only 2 game days, Est.)",
        highlight: "Super Bowl LXIII officially awarded to Allegiant Stadium, Las Vegas (Feb 2029). Longer gap before Spring Training yields a projected 9-day strict window!",
      },
    };

    cardsEl.innerHTML = ["2027", "2028", "2029"]
      .map((yr) => {
        const y = vac.years[yr];
        const info = yearNotes[yr];
        const bestNoSp = y.noSpringPreStreaks[0];
        return `
          <div class="kpi-card ${yr === "2027" ? "green" : "amber"}">
            <div class="card-header" style="margin-bottom:8px;">
              <span class="kpi-label">${yr} Vacation Outlook</span>
              ${info.badge}
            </div>
            <div class="kpi-value ${yr === "2027" ? "text-green" : "text-amber"}">${bestNoSp.days} Days (${bestNoSp.weeks} wks)</div>
            <div class="kpi-sub"><strong>Zero Regular/Postseason Window:</strong><br/>${info.topNoSpring}</div>
            <hr style="border:0;border-top:1px solid var(--border);margin:12px 0;" />
            <div class="small">
              <div><strong>Zero-Game Days in ${yr}:</strong> ${y.zeroGameDaysStrict} strict · ${y.zeroGameDaysNoSpringPre} excl. Spring/Pre · ${y.zeroGameDaysHighPriority} zero High-Priority</div>
              <div class="mt-1"><strong>Top Strict Zero-Game Streaks:</strong> ${info.topStrict}</div>
              <div class="mt-1"><strong>Best 3-Week Low-Impact Window:</strong> ${info.lowImpact3W}</div>
              <div class="mt-1 text-muted">${info.highlight}</div>
            </div>
            <div class="mt-2">
              <a class="btn btn-sm" href="vacation-windows.html?year=${yr}">View Full ${yr} Analysis &rarr;</a>
            </div>
          </div>
        `;
      })
      .join("");

    // Today's Snapshot (2026-11-25)
    const todayRec = daily.days.find((d) => d.date === FTV.TODAY_REF) || daily.days[0];
    const todayEvents = eventsData.events.filter((e) => e.date === todayRec.date);
    document.getElementById("today-date-badge").textContent = FTV.fmtDateNice(todayRec.date);

    const hpIntervals = FTV.mergeIntervals(
      todayEvents.filter((e) => e.highPriority).map((e) => [e.startMinPST, e.startMinPST + e.durationMin])
    );

    document.getElementById("today-snapshot").innerHTML = `
      <div class="grid grid-3 mb-2">
        <div>
          <div class="kpi-label">Daily Status</div>
          <div style="font-size:1.25rem;font-weight:800;margin-top:4px;">
            ${todayRec.freeStrict ? `<span class="text-green">100% FREE ALL DAY</span>` : `<span class="text-orange">${todayRec.eventCount} Scheduled Game(s)</span>`}
          </div>
          <div class="small text-muted">High Priority: ${todayRec.highPriorityCount} · Westwood One: ${todayRec.ww1Count}</div>
        </div>
        <div>
          <div class="kpi-label">Total Free Time (PST)</div>
          <div style="font-size:1.25rem;font-weight:800;margin-top:4px;" class="text-green">${FTV.fmtDuration(todayRec.freeMinutes)}</div>
          <div class="small text-muted">Busy Sports Window: ${FTV.fmtDuration(todayRec.busyMinutes)}</div>
        </div>
        <div style="display:flex;align-items:center;justify-content:flex-end;">
          <a class="btn btn-primary" href="scoreboard.html?date=${todayRec.date}">Inspect Full Scoreboard &rarr;</a>
        </div>
      </div>
      ${FTV.renderTimeline(todayRec.busyIntervalsPST, hpIntervals)}
      <div>
        <strong class="small">Exact Free-Time Windows Today (PST):</strong>
        <div class="window-chips">
          ${todayRec.freeWindowsText.map((w) => `<span class="window-chip">${FTV.esc(w)}</span>`).join("")}
        </div>
      </div>
      <div class="mt-2">
        ${todayEvents
          .map(
            (e) => `
            <div class="game-card ${e.highPriority ? "hp" : ""}">
              <div class="game-card-top">
                <div>
                  <span class="badge badge-league">${FTV.esc(e.league)}</span>
                  ${e.highPriority ? `<span class="badge badge-hp">HIGH PRIORITY</span>` : ""}
                  ${e.isWestwoodOne ? `<span class="badge badge-ww1">WESTWOOD ONE RADIO</span>` : ""}
                  ${FTV.statusBadge(e.status)}
                </div>
                <div class="small"><strong>${FTV.esc(e.officialTimePST || e.estimatedTimePST)}</strong> · Avg ${FTV.fmtDuration(e.durationMin)}</div>
              </div>
              <div class="game-title">${FTV.esc(e.title)}</div>
              <div class="game-meta">
                <span>Venue: ${FTV.esc(e.venue)}</span>
                <span>Radio: ${FTV.esc(e.radioStations)}</span>
                <span><a href="${FTV.esc(e.sourceUrl)}" target="_blank" rel="noopener">Official Source &nearr;</a></span>
              </div>
            </div>
          `
          )
          .join("")}
      </div>
    `;

    // Durations table
    document.getElementById("durations-tbody").innerHTML = meta.durations
      .map(
        (d) => `
        <tr>
          <td><strong>${FTV.esc(d.category)}</strong></td>
          <td><strong>${FTV.esc(d.display)}</strong> (${d.avgMinutes} min)</td>
          <td>${d.halftimeMinutes ? `${d.halftimeMinutes} min` : "None (Innings)"}</td>
          <td class="text-muted">${FTV.esc(d.basis)}</td>
          <td><a href="${FTV.esc(d.sourceUrl)}" target="_blank" rel="noopener">Official Source &nearr;</a></td>
        </tr>
      `
      )
      .join("");
  } catch (err) {
    document.getElementById("today-snapshot").innerHTML = `<div class="callout orange">Error loading data: ${FTV.esc(err.message)}</div>`;
  }
})();
