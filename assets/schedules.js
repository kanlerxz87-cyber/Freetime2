(async () => {
  FTV.renderChrome("schedules");

  const data = await FTV.loadJSON("data/all_events.json");
  const allEvents = data.events;
  const PAGE_SIZE = 100;
  let currentPage = 1;
  let filtered = [];

  const fYear = document.getElementById("f-year");
  const fLeague = document.getElementById("f-league");
  const fPriority = document.getElementById("f-priority");
  const fStatus = document.getElementById("f-status");
  const fSearch = document.getElementById("f-search");

  function applyFilters(resetPage = true) {
    const yr = fYear.value;
    const lg = fLeague.value;
    const pr = fPriority.value;
    const st = fStatus.value;
    const q = fSearch.value.trim().toLowerCase();

    filtered = allEvents.filter((e) => {
      if (yr !== "ALL" && String(e.year) !== yr) return false;
      if (lg !== "ALL" && e.league !== lg) return false;
      if (pr === "HP" && !e.highPriority) return false;
      if (pr === "WW1" && !e.isWestwoodOne) return false;
      if (st !== "ALL" && e.status !== st) return false;
      if (q) {
        const hay = `${e.date} ${e.title} ${e.away} ${e.home} ${e.venue} ${e.radioStations} ${e.phase} ${e.notes}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });

    if (resetPage) currentPage = 1;
    renderTable();
  }

  function renderPager(totalPages) {
    const html = `
      <button class="btn btn-sm" ${currentPage <= 1 ? "disabled" : ""} data-act="prev">&larr; Prev</button>
      <span class="small text-muted">Page <strong>${currentPage}</strong> of <strong>${Math.max(1, totalPages)}</strong></span>
      <button class="btn btn-sm" ${currentPage >= totalPages ? "disabled" : ""} data-act="next">Next &rarr;</button>
    `;
    ["pager-top", "pager-bottom"].forEach((id) => {
      const el = document.getElementById(id);
      el.innerHTML = html;
      el.querySelectorAll("button[data-act]").forEach((btn) => {
        btn.addEventListener("click", () => {
          if (btn.dataset.act === "prev" && currentPage > 1) currentPage--;
          if (btn.dataset.act === "next" && currentPage < totalPages) currentPage++;
          renderTable();
          window.scrollTo({ top: 0, behavior: "smooth" });
        });
      });
    });
  }

  function renderTable() {
    const total = filtered.length;
    const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    const start = (currentPage - 1) * PAGE_SIZE;
    const slice = filtered.slice(start, start + PAGE_SIZE);

    const summary = `Showing <strong>${total ? start + 1 : 0}–${Math.min(total, start + PAGE_SIZE)}</strong> of <strong>${total.toLocaleString()}</strong> matching records (out of ${allEvents.length.toLocaleString()} total indexed events)`;
    document.getElementById("results-summary").innerHTML = summary;
    document.getElementById("results-summary-bottom").innerHTML = summary;
    renderPager(totalPages);

    const tbody = document.getElementById("sched-tbody");
    if (!slice.length) {
      tbody.innerHTML = `<tr><td colspan="9" class="text-muted">No events match your current filters.</td></tr>`;
      return;
    }

    tbody.innerHTML = slice
      .map(
        (e) => `
        <tr class="${e.highPriority ? "row-hp" : ""}">
          <td style="white-space:nowrap;">
            <a href="scoreboard.html?date=${e.date}"><strong>${e.date}</strong></a>
          </td>
          <td>
            <span class="badge badge-league">${FTV.esc(e.league)}</span>
            <div class="small text-muted">${FTV.esc(e.phase)}</div>
          </td>
          <td>
            <strong>${FTV.esc(e.title)}</strong>
            <div class="small text-muted">${FTV.esc(e.venue)}</div>
          </td>
          <td style="white-space:nowrap;">
            ${e.officialTimePST ? `<strong>${FTV.esc(e.officialTimePST)}</strong>` : `<span class="text-dim">—</span>`}
          </td>
          <td style="white-space:nowrap;">
            ${e.estimatedTimePST ? `<span class="text-amber">${FTV.esc(e.estimatedTimePST)}</span>` : `<span class="text-dim">—</span>`}
          </td>
          <td style="white-space:nowrap;">
            ${FTV.fmtDuration(e.durationMin)}
            ${e.halftimeMin ? `<div class="small text-muted">HT: ${e.halftimeMin}m</div>` : ""}
          </td>
          <td>
            ${e.highPriority ? `<span class="badge badge-hp">HIGH PRIORITY</span> ` : ""}
            ${e.isWestwoodOne ? `<span class="badge badge-ww1">WW1</span> ` : ""}
            <div class="small text-muted">${FTV.esc(e.radioStations)}</div>
          </td>
          <td>${FTV.statusBadge(e.status)}</td>
          <td style="white-space:nowrap;">
            <a href="${FTV.esc(e.sourceUrl)}" target="_blank" rel="noopener">${FTV.esc(e.sourceLabel)} &nearr;</a>
          </td>
        </tr>
      `
      )
      .join("");
  }

  // Export CSV
  document.getElementById("btn-export-csv").addEventListener("click", () => {
    const cols = ["date", "league", "phase", "title", "venue", "officialTimePST", "estimatedTimePST", "durationMin", "halftimeMin", "highPriority", "isWestwoodOne", "radioStations", "status", "sourceUrl"];
    const lines = [cols.join(",")];
    for (const e of filtered) {
      lines.push(cols.map((c) => `"${String(e[c] ?? "").replace(/"/g, '""')}"`).join(","));
    }
    const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `freetime-vacation-schedule-${fYear.value}-${fLeague.value}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  });

  [fYear, fLeague, fPriority, fStatus].forEach((el) => el.addEventListener("change", () => applyFilters(true)));
  fSearch.addEventListener("input", () => applyFilters(true));

  applyFilters(true);
})();
