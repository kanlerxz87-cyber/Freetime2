(function () {
  const F = window.FT;
  const $ = (id) => document.getElementById(id);

  // Find maximal runs of consecutive days where predicate(day) is false (i.e. no game).
  function runsWithoutGame(fromDate, toDate, hasGame) {
    const runs = [];
    let start = null, n = 0;
    for (let d = fromDate; d <= toDate; d = F.addDays(d, 1)) {
      if (!hasGame(d)) {
        if (start === null) start = d;
        n++;
      } else if (start !== null) {
        runs.push({ from: start, to: F.addDays(d, -1), days: n });
        start = null; n = 0;
      }
    }
    if (start !== null) runs.push({ from: start, to: toDate, days: n });
    return runs.sort((a, b) => b.days - a.days).slice(0, 6);
  }

  function table(id, rows) {
    const tb = $(id).querySelector("tbody");
    tb.innerHTML = rows.length
      ? rows.map((r) => "<tr><td>" + F.fmtDayLong(r.from) + "</td><td>" + F.fmtDayLong(r.to) + "</td><td>" + r.days + "</td></tr>").join("")
      : '<tr><td colspan="3">None in this window.</td></tr>';
  }

  async function init() {
    try {
      const DATA = await F.loadAll();
      const mlbEv = DATA.events.filter((e) => e.category === "MLB");
      $("k-mlb").textContent = mlbEv.length.toLocaleString();
      const sfEv = mlbEv.filter((e) => e.mlbIds.some((id) => F.HIGH_MLB_IDS.includes(id)));
      $("k-sf").textContent = sfEv.length.toLocaleString();
      $("k-nat").textContent = DATA.snap.events.filter((e) => e.network && e.network.indexOf("Westwood One") === 0).length;
      $("k-hand").textContent = DATA.snap.events.length;

      if (DATA.mlb.errors.length) {
        $("liveNote").innerHTML = '<span class="badge b-unverified">UNVERIFIED</span> The MLB feed did not load in this browser (' + F.esc(DATA.mlb.errors.join("; ")) + '). The runs below are not available.';
        return;
      }
      $("liveNote").textContent = "MLB seasons loaded: " + DATA.mlb.loaded.join(", ") + ". Source: MLB Stats API (statsapi.mlb.com). Times are Pacific.";

      const sfDays = new Set(sfEv.map((e) => e.date));
      const allDays = new Set(mlbEv.map((e) => e.date));
      const sfRuns = runsWithoutGame("2027-03-01", "2027-11-30", (d) => sfDays.has(d));
      const allRuns = runsWithoutGame("2027-03-01", "2027-11-30", (d) => allDays.has(d));
      table("runsSF", sfRuns);
      table("runsAll", allRuns);
    } catch (err) {
      $("liveNote").textContent = "Could not load data: " + err.message;
    }
  }
  init();
})();
