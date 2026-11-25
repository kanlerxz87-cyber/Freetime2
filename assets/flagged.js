(async () => {
  FTV.renderChrome("flagged");

  const [flagsData, meta] = await Promise.all([
    FTV.loadJSON("data/flagged_items.json"),
    FTV.loadJSON("data/metadata.json"),
  ]);

  const items = flagsData.items;
  const highCnt = items.filter((i) => i.severity === "HIGH").length;
  const medCnt = items.filter((i) => i.severity === "MEDIUM").length;
  const lowCnt = items.filter((i) => i.severity === "LOW").length;

  document.getElementById("flag-kpis").innerHTML = `
    <div class="kpi-card orange">
      <div class="kpi-label">Total Flagged Audit Items</div>
      <div class="kpi-value text-orange">${items.length}</div>
      <div class="kpi-sub">${highCnt} High · ${medCnt} Medium · ${lowCnt} Low</div>
    </div>
    <div class="kpi-card blue">
      <div class="kpi-label">Verified Events Indexed</div>
      <div class="kpi-value">${meta.verifiedEventsCount.toLocaleString()}</div>
      <div class="kpi-sub">Directly from MLB Stats API, NFL, 49ers, WW1, Stanford &amp; Cal</div>
    </div>
    <div class="kpi-card amber">
      <div class="kpi-label">Clearly Flagged Estimated Events</div>
      <div class="kpi-value text-amber">${meta.estimatedEventsCount.toLocaleString()}</div>
      <div class="kpi-sub">Unreleased 2027 NFL/Postseason, 2028 &amp; 2029 schedules</div>
    </div>
  `;

  const sevSel = document.getElementById("flag-severity");

  function render() {
    const sev = sevSel.value;
    const list = sev === "ALL" ? items : items.filter((i) => i.severity === sev);
    document.getElementById("flag-count-lbl").textContent = `Showing ${list.length} of ${items.length} flagged audit items`;

    document.getElementById("flags-tbody").innerHTML = list
      .map(
        (f) => `
        <tr class="${f.severity === "HIGH" ? "row-hp" : ""}">
          <td style="white-space:nowrap;">
            <strong>${FTV.esc(f.id)}</strong>
            <div class="mt-1">
              <span class="badge ${
                f.severity === "HIGH" ? "badge-busy" : f.severity === "MEDIUM" ? "badge-est" : "badge-league"
              }">${FTV.esc(f.severity)}</span>
            </div>
          </td>
          <td>
            <strong>${FTV.esc(f.category)}</strong>
            <div class="small text-muted mt-1">${FTV.esc(f.scope)}</div>
          </td>
          <td>${FTV.esc(f.issue)}</td>
          <td class="text-muted">${FTV.esc(f.actionRequired)}</td>
          <td style="white-space:nowrap;">
            <a href="${FTV.esc(f.sourceUrl)}" target="_blank" rel="noopener">${FTV.esc(f.sourceLabel)} &nearr;</a>
          </td>
        </tr>
      `
      )
      .join("");
  }

  sevSel.addEventListener("change", render);
  render();
})();
