(async () => {
  FTV.renderChrome("radio");

  const [stationsData, ww1Data] = await Promise.all([
    FTV.loadJSON("data/radio_stations.json"),
    FTV.loadJSON("data/westwood_one_2026.json"),
  ]);

  document.getElementById("stations-tbody").innerHTML = stationsData.stations
    .map(
      (s) => `
      <tr class="${s.priority === "HIGH" ? "row-hp" : ""}">
        <td style="white-space:nowrap;">
          <strong>${FTV.esc(s.frequency)}</strong>
          <div class="small text-muted">${FTV.esc(s.callSign)} (${FTV.esc(s.band)})</div>
        </td>
        <td>
          <strong>${FTV.esc(s.branding)}</strong>
          <div class="small text-muted">${FTV.esc(s.transmitter)}</div>
        </td>
        <td>
          <span class="badge ${
            s.outerSunset94122.startsWith("EXCELLENT")
              ? "badge-free"
              : s.outerSunset94122.startsWith("GOOD")
              ? "badge-verified"
              : "badge-est"
          }">${FTV.esc(s.outerSunset94122.split(" ")[0])}</span>
          <div class="small text-muted mt-1">${FTV.esc(s.outerSunset94122)}</div>
        </td>
        <td>
          <ul style="margin:0;padding-left:16px;">
            ${s.liveSports.map((sp) => `<li>${FTV.esc(sp)}</li>`).join("")}
          </ul>
        </td>
        <td>
          ${
            s.priority === "HIGH"
              ? `<span class="badge badge-hp">HIGH PRIORITY</span>`
              : `<span class="badge badge-league">SECONDARY</span>`
          }
          <div class="mt-1">${s.verified ? `<span class="badge badge-verified">VERIFIED</span>` : `<span class="badge badge-est">FLAGGED</span>`}</div>
        </td>
        <td style="white-space:nowrap;">
          <a href="${FTV.esc(s.sourceUrl)}" target="_blank" rel="noopener">${FTV.esc(s.sourceLabel)} &nearr;</a>
        </td>
      </tr>
    `
    )
    .join("");

  document.getElementById("ww1-tbody").innerHTML = ww1Data.broadcasts
    .map(
      (b) => `
      <tr class="${b.is49ers ? "row-hp" : ""}">
        <td style="white-space:nowrap;">
          <a href="scoreboard.html?date=${b.date}"><strong>${b.date}</strong></a>
        </td>
        <td><span class="badge badge-league">${FTV.esc(b.week)}</span></td>
        <td>
          <strong>${FTV.esc(b.broadcastLabel)}</strong>
          ${b.is49ers ? ` <span class="badge badge-hp">49ERS</span>` : ""}
        </td>
        <td>
          <strong>${FTV.esc(b.matchup)}</strong>
          <div class="small text-muted">${FTV.esc(b.venue)}</div>
        </td>
        <td style="white-space:nowrap;">
          <strong>${FTV.esc(b.airTimePST)}</strong>
          <div class="small text-muted">${FTV.esc(b.airTimeET)}</div>
        </td>
        <td style="white-space:nowrap;">${FTV.esc(b.kickoffPST)}</td>
        <td class="small text-muted">${FTV.esc(b.sfAffiliate)}</td>
        <td style="white-space:nowrap;">
          <a href="${FTV.esc(b.sourceUrl)}" target="_blank" rel="noopener">Official Page &nearr;</a>
        </td>
      </tr>
    `
    )
    .join("");
})();
