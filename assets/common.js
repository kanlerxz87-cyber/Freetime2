/* Shared helpers & navigation for FREE TIME VACATION dashboard */
window.FTV = (() => {
  const TODAY_REF = "2026-11-25";

  function esc(str) {
    if (str === null || str === undefined) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function fmtMin(m) {
    if (m <= 0) return "12:00 AM";
    if (m >= 1440) return "11:59 PM";
    const h = Math.floor(m / 60) % 24;
    const mn = m % 60;
    const ampm = h < 12 ? "AM" : "PM";
    const h12 = h % 12 === 0 ? 12 : h % 12;
    return `${h12}:${String(mn).padStart(2, "0")} ${ampm}`;
  }

  function fmtDuration(mins) {
    const h = Math.floor(mins / 60);
    const m = mins % 60;
    if (h === 0) return `${m}m`;
    if (m === 0) return `${h}h`;
    return `${h}h ${m}m`;
  }

  function fmtDateNice(iso) {
    const [y, m, d] = iso.split("-").map(Number);
    const dt = new Date(Date.UTC(y, m - 1, d));
    return dt.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      year: "numeric",
      timeZone: "UTC",
    });
  }

  function mergeIntervals(intervals) {
    const clean = [];
    for (const [s, e] of intervals) {
      const s2 = Math.max(0, Math.min(1440, Math.round(s)));
      const e2 = Math.max(0, Math.min(1440, Math.round(e)));
      if (e2 > s2) clean.push([s2, e2]);
    }
    if (!clean.length) return [];
    clean.sort((a, b) => a[0] - b[0]);
    const out = [clean[0]];
    for (let i = 1; i < clean.length; i++) {
      const [s, e] = clean[i];
      if (s <= out[out.length - 1][1]) {
        out[out.length - 1][1] = Math.max(out[out.length - 1][1], e);
      } else {
        out.push([s, e]);
      }
    }
    return out;
  }

  function complementIntervals(busy) {
    if (!busy.length) return [[0, 1440]];
    const free = [];
    let cur = 0;
    for (const [s, e] of busy) {
      if (s > cur) free.push([cur, s]);
      cur = Math.max(cur, e);
    }
    if (cur < 1440) free.push([cur, 1440]);
    return free;
  }

  function statusBadge(status) {
    if (status === "VERIFIED") {
      return `<span class="badge badge-verified">VERIFIED</span>`;
    }
    if (status === "VERIFIED_DATE_TIME_TBD") {
      return `<span class="badge badge-est">DATE VERIFIED · TIME TBD</span>`;
    }
    return `<span class="badge badge-est">ESTIMATED (UNRELEASED)</span>`;
  }

  function renderTimeline(busyIntervals, hpIntervals = []) {
    const hpBlocks = hpIntervals
      .map(([s, e]) => {
        const left = (s / 1440) * 100;
        const width = Math.max(0.5, ((e - s) / 1440) * 100);
        return `<div class="timeline-busy hp" style="left:${left.toFixed(2)}%;width:${width.toFixed(2)}%" title="High-Priority Live Broadcast: ${fmtMin(s)} – ${fmtMin(e)} PST"></div>`;
      })
      .join("");

    const stdBlocks = busyIntervals
      .map(([s, e]) => {
        const left = (s / 1440) * 100;
        const width = Math.max(0.5, ((e - s) / 1440) * 100);
        return `<div class="timeline-busy" style="left:${left.toFixed(2)}%;width:${width.toFixed(2)}%" title="Scheduled Sports: ${fmtMin(s)} – ${fmtMin(e)} PST"></div>`;
      })
      .join("");

    return `
      <div class="timeline-wrap">
        <div class="timeline-bar" aria-label="24-hour PST Free vs Busy Timeline">
          ${stdBlocks}
          ${hpBlocks}
        </div>
        <div class="timeline-axis">
          <span>12 AM PST</span>
          <span>4 AM</span>
          <span>8 AM</span>
          <span>12 PM</span>
          <span>4 PM</span>
          <span>8 PM</span>
          <span>11:59 PM</span>
        </div>
      </div>
    `;
  }

  function renderChrome(activePage) {
    const navItems = [
      { id: "home", href: "index.html", label: "Executive Summary" },
      { id: "scoreboard", href: "scoreboard.html", label: "Daily Scoreboard (PST)" },
      { id: "vacation", href: "vacation-windows.html", label: "2027–2029 Vacations" },
      { id: "schedules", href: "schedules.html", label: "All Schedules" },
      { id: "radio", href: "radio-bayarea.html", label: "SF 94122 AM/FM Radio" },
      { id: "flagged", href: "flagged-review.html", label: "Flagged for Review", isFlag: true },
    ];

    const headerEl = document.getElementById("site-header");
    if (headerEl) {
      headerEl.className = "site-header";
      headerEl.innerHTML = `
        <div class="header-inner">
          <a class="brand" href="index.html">
            <span class="brand-badge">94122 PST</span>
            <span>
              FREE TIME VACATION
              <span class="brand-sub">SF Bay Area Live AM/FM Sports Radio Planner (2026–2029)</span>
            </span>
          </a>
          <nav class="main-nav" aria-label="Main navigation">
            ${navItems
              .map(
                (n) =>
                  `<a href="${n.href}" class="${n.id === activePage ? "active" : ""}">${n.label}${
                    n.isFlag ? `<span class="nav-flag-pill">Audit</span>` : ""
                  }</a>`
              )
              .join("")}
          </nav>
        </div>
      `;
    }

    const footerEl = document.getElementById("site-footer");
    if (footerEl) {
      footerEl.className = "site-footer";
      footerEl.innerHTML = `
        <div class="footer-inner">
          <div>
            <strong>FREE TIME VACATION</strong> · Outer Sunset, San Francisco (94122) · All calendar times displayed in <strong>PST (UTC-8)</strong>.<br/>
            Verified against official primary sources (MLB Stats API / MLB.com, NFL.com, 49ers.com, Westwood One Sports, GoStanford.com, CalBears.com, KNBR) on <strong>Nov 25, 2026</strong>.
          </div>
          <div>
            <a href="flagged-review.html">Flagged for Review</a> ·
            <a href="radio-bayarea.html">Bay Area Radio Directory</a> ·
            <a href="https://github.com/kanlerxz87-cyber/Freetime2" target="_blank" rel="noopener">GitHub Repository</a>
          </div>
        </div>
      `;
    }
  }

  async function loadJSON(path) {
    const res = await fetch(path);
    if (!res.ok) throw new Error(`Failed to load ${path}: HTTP ${res.status}`);
    return res.json();
  }

  return {
    TODAY_REF,
    esc,
    fmtMin,
    fmtDuration,
    fmtDateNice,
    mergeIntervals,
    complementIntervals,
    statusBadge,
    renderTimeline,
    renderChrome,
    loadJSON,
  };
})();
