#!/usr/bin/env node
// Build check for the scoreboard site in scoreboard/ (served at /scoreboard/).
// 1. Every internal href/src resolves to a file in scoreboard/ (and #Fx anchors to a known flag).
// 2. Every JSON file parses, every JS file parses.
// 3. Every data row in snapshot.json has an https source_url, and every flag has a source.
// Exit code 1 on any failure, so a broken site cannot be published silently.
import { readFileSync, readdirSync, existsSync, statSync } from "node:fs";
import { join, dirname, resolve } from "node:path";

const root = resolve(new URL("..", import.meta.url).pathname, "scoreboard");
const problems = [];
const ok = [];

function walk(dir) {
  return readdirSync(dir).flatMap((f) => {
    const p = join(dir, f);
    return statSync(p).isDirectory() ? walk(p) : [p];
  });
}

const files = walk(root);
const htmlFiles = files.filter((f) => f.endsWith(".html"));
const jsonFiles = files.filter((f) => f.endsWith(".json"));
const jsFiles = files.filter((f) => f.endsWith(".js"));

// 2. parse JSON / JS
for (const f of jsonFiles) {
  try { JSON.parse(readFileSync(f, "utf8")); ok.push("json ok " + f); }
  catch (e) { problems.push("JSON parse failed: " + f + " — " + e.message); }
}
for (const f of jsFiles) {
  try { new Function(readFileSync(f, "utf8")); ok.push("js ok " + f); }
  catch (e) { problems.push("JS syntax error: " + f + " — " + e.message); }
}

// 3. snapshot rows and flags
const snapPath = join(root, "data", "snapshot.json");
const snap = JSON.parse(readFileSync(snapPath, "utf8"));
const flagIds = new Set(snap.irregularities.map((i) => i.id));
for (const e of snap.events) {
  if (!/^https:\/\//.test(e.source_url || "")) problems.push("Row without https source_url: " + e.id);
  if (e.flag && !flagIds.has(e.flag)) problems.push("Row " + e.id + " references unknown flag " + e.flag);
}
for (const i of snap.irregularities) {
  if (!i.sources || !i.sources.length) problems.push("Flag without sources: " + i.id);
}
ok.push("snapshot rows checked: " + snap.events.length + " · flags: " + snap.irregularities.length);

// 1. internal links in HTML
const attrRe = /(?:href|src)="([^"]+)"/g;
for (const f of htmlFiles) {
  const html = readFileSync(f, "utf8");
  let m;
  while ((m = attrRe.exec(html))) {
    const raw = m[1].replace(/&amp;/g, "&");
    if (/^(https?:|mailto:|tel:|data:)/.test(raw)) continue;
    if (raw.startsWith("#")) continue;
    const [pathPart, hash] = raw.split("#");
    const target = resolve(dirname(f), pathPart.split("?")[0]);
    if (!target.startsWith(root)) { problems.push("Link escapes scoreboard/: " + raw + " in " + f); continue; }
    if (!existsSync(target)) { problems.push("Broken internal link: " + raw + " in " + f.replace(root, "scoreboard")); continue; }
    if (hash && /flagged\.html$/.test(pathPart) && /^F\d+$/.test(hash) && !flagIds.has(hash)) {
      problems.push("Broken flag anchor: " + raw + " in " + f.replace(root, "scoreboard"));
    }
  }
  ok.push("links checked " + f.replace(root, "scoreboard"));
}

for (const line of ok) console.log("  ✓ " + line);
if (problems.length) {
  console.error("\nBUILD CHECK FAILED:");
  for (const p of problems) console.error("  ✗ " + p);
  process.exit(1);
}
console.log("\nBUILD CHECK PASSED: " + htmlFiles.length + " pages, " + jsFiles.length + " scripts, " + jsonFiles.length + " data files — no broken links.");
