(function () {
  const F = window.FT;
  const $ = (id) => document.getElementById(id);
  const mode = document.body.dataset.page;

  function eventRows(events) {
    return events.map((e) => {
      const date = e.date ? F.fmtDayShort(e.date) : "TBD";
      const time = e.time_pt ? F.fmtClockHHMM(e.time_pt) : "Not published";
      const pub = e.time_published ? '<div class="note">Published: ' + F.esc(e.time_published) + "</div>" : "";
      const flag = e.flag ? ' <a href="flagged.html#' + e.flag + '">' + e.flag + "</a>" : "";
      const result = e.result ? F.esc(e.result) : "";
      const pr = e.priority === "HIGH" ? F.badge("high", "High") : F.badge("unverified", "Standard");
      return '<tr class="' + (e.priority === "HIGH" ? "hi" : "") + '"><td>' + date + "</td><td>" + (time || "—") + pub + "</td><td><b>" + F.esc(e.title) +
        "</b>" + (e.venue ? '<div class="note">' + F.esc(e.venue) + "</div>" : "") + "</td><td>" + F.esc(e.network || "—") + "</td><td>" + pr +
        "</td><td>" + F.statusBadge(e.status) + flag + "</td><td>" + result + '</td><td><a href="' + F.esc(e.source_url) + '" target="_blank" rel="noopener">' +
        F.esc(e.source_name) + "</a></td></tr>";
    }).join("");
  }
  const EVENT_HEAD = "<tr><th>Date</th><th>Start (PT)</th><th>Game</th><th>Broadcast</th><th>Priority</th><th>Status</th><th>Result</th><th>Source</th></tr>";

  async function snapshot() { return F.getJSON("data/snapshot.json"); }

  async function renderNFL() {
    const s = await snapshot();
    const nfl = s.events.filter((e) => e.category === "NFL");
    const radio = nfl.filter((e) => e.network && e.network.indexOf("Westwood One") === 0);
    const sf = nfl.filter((e) => !(e.network && e.network.indexOf("Westwood One") === 0));
    $("nflRadio").querySelector("thead").innerHTML = EVENT_HEAD;
    $("nflRadio").querySelector("tbody").innerHTML = eventRows(radio);
    $("nflSF").querySelector("thead").innerHTML = EVENT_HEAD;
    $("nflSF").querySelector("tbody").innerHTML = eventRows(sf);
    $("nflCount").textContent = radio.length + " Westwood One national radio games and " + sf.length + " 49ers rows loaded. The full NFL slate is not loaded.";
  }

  async function renderNCAAF() {
    const s = await snapshot();
    const stan = s.events.filter((e) => e.category === "NCAAF" && e.id.indexOf("STAN") > -1);
    const cal = s.events.filter((e) => e.category === "NCAAF" && e.id.indexOf("CAL") > -1);
    $("stanTable").querySelector("thead").innerHTML = EVENT_HEAD;
    $("stanTable").querySelector("tbody").innerHTML = eventRows(stan);
    $("calTable").querySelector("thead").innerHTML = EVENT_HEAD;
    $("calTable").querySelector("tbody").innerHTML = eventRows(cal);
  }

  async function renderMLB() {
    const t = await F.getJSON("data/mlb-teams.json");
    const rows = t.teams.slice().sort((a, b) => a.name.localeCompare(b.name)).map((c) => {
      const hi = c.priority === "HIGH";
      return '<tr class="' + (hi ? "hi" : "") + '"><td><b>' + F.esc(c.name) + "</b>" + (hi ? ' ' + F.badge("high", "High priority") : "") + "</td><td>" + F.esc(c.abbr) +
        "</td><td>" + F.esc(c.venue) + "</td><td>" + F.esc(c.division) + '</td><td>' + (c.id === 137 || c.id === 133 ? F.badge("verified", "2027 games checked in MLB feed") : F.badge("unverified", "2027 league release; club games load live")) +
        '</td><td><a href="' + F.esc(c.api) + '" target="_blank" rel="noopener">MLB Stats API team record</a></td></tr>';
    }).join("");
    $("mlbTable").querySelector("tbody").innerHTML = rows;
    $("mlbCount").textContent = t.teams.length + " clubs listed. Source: " + t.source;
  }

  async function renderFlagged() {
    const s = await snapshot();
    const body = s.irregularities.map((i) => {
      const srcs = i.sources.map((x) => {
        const isUrl = /^https?:\/\//.test(x.url);
        return isUrl ? '<a href="' + F.esc(x.url) + '" target="_blank" rel="noopener">' + F.esc(x.name) + "</a>" : F.esc(x.name) + " (" + F.esc(x.url) + ")";
      }).join("<br>");
      const linked = s.events.filter((e) => e.flag === i.id);
      const rel = linked.length ? '<div class="note">Rows affected: ' + linked.map((e) => F.esc(e.title)).join("; ") + "</div>" : "";
      return '<tr id="' + i.id + '"><td><b>' + F.esc(i.id) + "</b></td><td><b>" + F.esc(i.title) + "</b>" + rel + "</td><td>" + F.esc(i.detail) + "</td><td>" + srcs + "</td></tr>";
    }).join("");
    $("flagTable").querySelector("tbody").innerHTML = body;
  }

  const renderers = { nfl: renderNFL, ncaaf: renderNCAAF, mlb: renderMLB, flagged: renderFlagged };
  if (renderers[mode]) {
    renderers[mode]().catch((err) => {
      const box = $("pageError");
      if (box) { box.hidden = false; box.textContent = "Could not load the data: " + err.message; }
    });
  }
})();
