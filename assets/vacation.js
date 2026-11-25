(async () => {
  FTV.renderChrome("vacation");

  const MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
  ];

  const [vacData, dailyData] = await Promise.all([
    FTV.loadJSON("data/vacation_windows.json"),
    FTV.loadJSON("data/daily_summary.json"),
  ]);

  const params = new URLSearchParams(window.location.search);
  let activeYear = params.get("year") || "2027";
  if (!["2027", "2028", "2029"].includes(activeYear)) activeYear = "2027";

  const modeSel = document.getElementById("heatmap-mode");
  const tabs = document.querySelectorAll("#year-tabs button");

  const yearCallouts = {
    "2027": {
      cls: "green",
      html: `<strong>2027 VERIFIED INSIGHT:</strong> Super Bowl LXI is officially <strong>Sun, Feb 14, 2027</strong> (SoFi Stadium), MLB Spring Training opens officially <strong>Fri, Feb 19, 2027</strong>, and MLB Regular Season Opening Night is officially <strong>Wed, Mar 24, 2027</strong>.
      <br/>&bull; <strong>Best Multi-Week Vacation (Skip Spring Training):</strong> <strong>Mon, Feb 15 – Tue, Mar 23, 2027 (37 consecutive days / 5+ weeks, 100% VERIFIED!)</strong>.
      <br/>&bull; <strong>Best 2–3 Week Strict Window:</strong> <strong>Feb 1 – Feb 18, 2027 (18 days)</strong> has <strong>16 completely zero-game days</strong> (only Pro Bowl Games &amp; Super Bowl LXI) — and <strong>Feb 1 – Feb 13</strong> has <strong>13 consecutive days with zero High-Priority Bay Area broadcasts</strong>.
      <br/>&bull; <strong>Mid-Summer Break:</strong> <strong>Wed, Jul 14, 2027</strong> is a verified zero-game All-Star Break day (Jul 12 has only HR Derby; Jul 15 has only 1 game: Braves @ Red Sox).`,
    },
    "2028": {
      cls: "amber",
      html: `<strong>2028 ESTIMATED INSIGHT + ORACLE PARK ALL-STAR ALERT:</strong> Neither 2028 MLB nor 2027–28 NFL schedules are released yet (all 2028 dates are clearly marked <em>Estimated</em>).
      <br/>&bull; <strong>Best Multi-Week Vacation (Skip Spring Training):</strong> Projected <strong>Mon, Feb 14 – Wed, Mar 22, 2028 (~38 consecutive days, Est.)</strong> after Super Bowl LXII in Atlanta (planned Feb 13, 2028).
      <br/>&bull; <strong>HUGE JULY 2028 BAY AREA ALERT:</strong> MLB officially awarded the <strong>2028 All-Star Game to the SF Giants at Oracle Park</strong> (July 2028) and explicitly noted coordination with the <strong>2028 Los Angeles Summer Olympics (Jul 14–30, 2028)</strong>! Monitor MLB's July 2027 schedule release — if MLB pauses for Olympic baseball, an unprecedented July 2028 MLB-free window could open!`,
    },
    "2029": {
      cls: "amber",
      html: `<strong>2029 ESTIMATED INSIGHT:</strong> 2029 MLB and 2028–29 NFL schedules are not yet released (marked <em>Estimated</em>).
      <br/>&bull; <strong>Super Bowl LXIII</strong> is officially awarded to <strong>Allegiant Stadium, Las Vegas (Feb 2029)</strong> (est. Sun, Feb 11, 2029).
      <br/>&bull; <strong>Best Multi-Week Vacation (Skip Spring Training):</strong> Projected <strong>Mon, Feb 12 – Wed, Mar 28, 2029 (~45 consecutive days / 6+ weeks, Est.)</strong>.
      <br/>&bull; <strong>Strict Mode Highlight:</strong> Because Feb 11 is an earlier Super Bowl Sunday, 2029 projects a <strong>9-day strict zero-game streak (Feb 12–20, 2029)</strong> — over 1 full week even INCLUDING MLB Spring Training!`,
    },
  };

  function render() {
    tabs.forEach((b) => b.classList.toggle("active-tab", b.dataset.year === activeYear));
    const y = vacData.years[activeYear];
    const yrNum = Number(activeYear);
    const mode = modeSel.value;

    document.getElementById("heatmap-year-lbl").textContent = activeYear;

    // KPIs
    const topNoSp = y.noSpringPreStreaks[0];
    const topStrict = y.strictStreaks[0];
    document.getElementById("vac-kpis").innerHTML = `
      <div class="kpi-card green">
        <div class="kpi-label">Longest Zero-Regular-Season Window</div>
        <div class="kpi-value text-green">${topNoSp.days} Days</div>
        <div class="kpi-sub">${FTV.fmtDateNice(topNoSp.startDate)} &ndash; ${FTV.fmtDateNice(topNoSp.endDate)}</div>
      </div>
      <div class="kpi-card blue">
        <div class="kpi-label">Longest Strict Zero-Game Streak</div>
        <div class="kpi-value">${topStrict.days} Days</div>
        <div class="kpi-sub">${FTV.fmtDateNice(topStrict.startDate)} &ndash; ${FTV.fmtDateNice(topStrict.endDate)}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Total Zero-Game Days (${activeYear})</div>
        <div class="kpi-value">${y.zeroGameDaysStrict} <span class="small text-muted">/ ${y.totalDays}</span></div>
        <div class="kpi-sub">${y.zeroGameDaysNoSpringPre} days excl. Spring/Preseason</div>
      </div>
      <div class="kpi-card orange">
        <div class="kpi-label">Zero High-Priority Bay Area Days</div>
        <div class="kpi-value text-orange">${y.zeroGameDaysHighPriority} Days</div>
        <div class="kpi-sub">${y.zeroGameDaysHighPriorityNoSpring} days excl. Spring/Preseason</div>
      </div>
    `;

    // Note
    const note = yearCallouts[activeYear];
    document.getElementById("vac-note").innerHTML = `<div class="callout ${note.cls}">${note.html}</div>`;

    // Streaks tables
    const renderRows = (list) =>
      list
        .slice(0, 10)
        .map(
          (s) => `
          <tr class="${s.days >= 7 ? "row-free" : ""}">
            <td><strong>${FTV.fmtDateNice(s.startDate)}</strong> &rarr; <strong>${FTV.fmtDateNice(s.endDate)}</strong></td>
            <td><strong>${s.days} days</strong> (${s.weeks} wks)</td>
            <td>${
              s.verifiedBasis.startsWith("Official")
                ? `<span class="badge badge-verified">VERIFIED</span>`
                : `<span class="badge badge-est">ESTIMATED</span>`
            }</td>
            <td><a class="btn btn-sm" href="scoreboard.html?date=${s.startDate}">Open &rarr;</a></td>
          </tr>
        `
        )
        .join("");

    document.getElementById("tbody-nospring").innerHTML = renderRows(y.noSpringPreStreaks);
    document.getElementById("tbody-strict").innerHTML = renderRows(y.strictStreaks);

    // Rolling 1-week, 2-week, 3-week strict windows
    const buckets = [
      { title: "Best 1-Week (7-Day) Strict Windows", data: y.best1WeekStrict },
      { title: "Best 2-Week (14-Day) Strict Windows", data: y.best2WeekStrict },
      { title: "Best 3-Week (21-Day) Strict Windows", data: y.best3WeekStrict },
    ];
    document.getElementById("rolling-windows-grid").innerHTML = buckets
      .map(
        (b) => `
        <div class="card">
          <h3 class="mb-2">${b.title}</h3>
          ${b.data
            .slice(0, 4)
            .map(
              (w, idx) => `
              <div class="game-card ${idx === 0 ? "hp" : ""}" style="border-left-color:${w.gameDays === 0 ? "var(--green)" : "var(--blue)"};">
                <div class="game-card-top">
                  <strong>#${idx + 1}: ${w.startDate} &rarr; ${w.endDate}</strong>
                  <span class="badge ${w.gameDays <= 2 ? "badge-free" : "badge-est"}">${w.zeroGameDays}/${w.windowDays} FREE</span>
                </div>
                <div class="small text-muted mt-1">
                  Game days inside window: <strong>${w.gameDays}</strong> (High-Priority: ${w.highPriorityDays})
                  ${
                    w.busyDates.length && w.busyDates.length <= 6
                      ? `<br/>Busy dates: ${w.busyDates
                          .map((bd) => `<a href="scoreboard.html?date=${bd}">${bd.slice(5)}</a>`)
                          .join(", ")}`
                      : ""
                  }
                </div>
                <div class="mt-1">
                  <a class="small" href="scoreboard.html?date=${w.startDate}">Inspect start date on scoreboard &rarr;</a>
                </div>
              </div>
            `
            )
            .join("")}
        </div>
      `
      )
      .join("");

    // 12-Month Heatmap
    const yrDays = dailyData.days.filter((d) => d.year === yrNum);
    const byMonth = new Map();
    for (const d of yrDays) {
      if (!byMonth.has(d.month)) byMonth.set(d.month, []);
      byMonth.get(d.month).push(d);
    }

    let hmHtml = "";
    for (let m = 1; m <= 12; m++) {
      const mDays = byMonth.get(m) || [];
      const freeCnt = mDays.filter((d) =>
        mode === "noSpring" ? d.freeNoSpringPre : mode === "highPriority" ? d.freeHighPriority : d.freeStrict
      ).length;
      const firstDow = new Date(Date.UTC(yrNum, m - 1, 1)).getUTCDay();
      let cells = "";
      for (let i = 0; i < firstDow; i++) cells += `<div></div>`;
      for (const d of mDays) {
        const isFree =
          mode === "noSpring" ? d.freeNoSpringPre : mode === "highPriority" ? d.freeHighPriority : d.freeStrict;
        const cls = isFree ? "free" : d.highPriorityCount > 0 ? "busy-hp" : "busy";
        const dayNum = Number(d.date.slice(8, 10));
        const tip = `${d.date}: ${isFree ? "FREE (0 games)" : `${d.eventCount} items, ${d.highPriorityCount} HP`} — Free ${FTV.fmtDuration(d.freeMinutes)}`;
        cells += `<a class="mini-cell ${cls}" href="scoreboard.html?date=${d.date}" title="${FTV.esc(tip)}">${dayNum}</a>`;
      }
      hmHtml += `
        <div class="mini-month">
          <h4><span>${MONTHS[m - 1]} ${yrNum}</span><span class="small ${freeCnt > 0 ? "text-green" : "text-muted"}">${freeCnt} free</span></h4>
          <div class="mini-grid">${cells}</div>
        </div>
      `;
    }
    document.getElementById("year-heatmap").innerHTML = hmHtml;
  }

  tabs.forEach((b) =>
    b.addEventListener("click", () => {
      activeYear = b.dataset.year;
      const url = new URL(window.location.href);
      url.searchParams.set("year", activeYear);
      window.history.replaceState({}, "", url);
      render();
    })
  );
  modeSel.addEventListener("change", render);

  render();
})();
