// Cloudflare Worker — live data engine for the Jetterix dashboard (Coolizi-parity feature set).
// Holds the GSC service-account key as SECRET (GSC_SA_JSON). Mints RS256 JWT, queries Search Console LIVE,
// returns: summary, daily(28d), hourly(24h), per-geo(page-path), device, queries, brand, opportunities,
// cannibalization, index status + funnel, milestones. ?start=YYYY-MM-DD&end=YYYY-MM-DD (default last 7d).
const PROP = "sc-domain:tryjetterix.com";
const PROP_ENC = "sc-domain%3Atryjetterix.com";
const SA_URL = `https://www.googleapis.com/webmasters/v3/sites/${PROP_ENC}/searchAnalytics/query`;
const INSPECT_URL = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect";
const GEOS = ["us", "uk", "au", "de", "fr"];
const URLS = ["https://tryjetterix.com/"].concat(GEOS.map(g => `https://tryjetterix.com/${g}/`));
const GEO_META = { us: ["USA", "🇺🇸"], uk: ["UK", "🇬🇧"], au: ["Australia", "🇦🇺"], de: ["DACH", "🇩🇪"], fr: ["France", "🇫🇷"] };

const ymd = d => (typeof d === "string" ? d : d.toISOString().slice(0, 10));
const addDays = (s, n) => { const d = new Date(ymd(s) + "T00:00:00Z"); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
const b64url = buf => btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const enc = new TextEncoder();
function pemToDer(pem){ const b = pem.replace(/-----[^-]+-----/g, "").replace(/\s+/g, ""); const bin = atob(b); const u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return u.buffer; }
async function getToken(sa){
  const now = Math.floor(Date.now() / 1000);
  const header = b64url(enc.encode(JSON.stringify({ alg: "RS256", typ: "JWT" })));
  const claim = b64url(enc.encode(JSON.stringify({ iss: sa.client_email, scope: "https://www.googleapis.com/auth/webmasters.readonly", aud: "https://oauth2.googleapis.com/token", exp: now + 3600, iat: now })));
  const key = await crypto.subtle.importKey("pkcs8", pemToDer(sa.private_key), { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["sign"]);
  const sig = b64url(await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, enc.encode(header + "." + claim)));
  const r = await fetch("https://oauth2.googleapis.com/token", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${header}.${claim}.${sig}` });
  const j = await r.json(); if (!j.access_token) throw new Error("token: " + JSON.stringify(j)); return j.access_token;
}
async function saQ(tok, dims, { state = "all", start, end } = {}){
  const body = { startDate: ymd(start), endDate: ymd(end), dimensions: dims, rowLimit: 2000, dataState: state };
  const r = await fetch(SA_URL, { method: "POST", headers: { Authorization: "Bearer " + tok, "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (!r.ok) return []; return (await r.json()).rows || [];
}
const rf = r => ({ keys: r.keys, impr: Math.round(r.impressions || 0), clicks: Math.round(r.clicks || 0), ctr: Math.round((r.ctr || 0) * 10000) / 100, pos: Math.round((r.position || 0) * 10) / 10 });
async function inspect(tok, url){
  try {
    const r = await fetch(INSPECT_URL, { method: "POST", headers: { Authorization: "Bearer " + tok, "Content-Type": "application/json" }, body: JSON.stringify({ inspectionUrl: url, siteUrl: PROP, languageCode: "en" }) });
    if (!r.ok) return { url, verdict: "ERR", coverage: `HTTP ${r.status}`, lastCrawl: null };
    const x = ((await r.json()).inspectionResult || {}).indexStatusResult || {};
    return { url, verdict: x.verdict || "?", coverage: x.coverageState || "Unknown", lastCrawl: x.lastCrawlTime || null };
  } catch (e) { return { url, verdict: "ERR", coverage: "timeout", lastCrawl: null }; }
}
async function getIndex(tok){
  try {
    const cache = caches.default, ck = new Request("https://jx-cache.local/index-status-v2");
    const hit = await cache.match(ck); if (hit) return await hit.json();
    const idx = await Promise.all(URLS.map(u => inspect(tok, u)));
    await cache.put(ck, new Response(JSON.stringify(idx), { headers: { "Cache-Control": "max-age=7200", "Content-Type": "application/json" } }));
    return idx;
  } catch (e) { return await Promise.all(URLS.map(u => inspect(tok, u))); }
}
const geoOf = url => { for (const g of GEOS) if (url.includes(`/${g}/`)) return g; return null; };
const wpos = rows => { const i = rows.reduce((a, r) => a + r.impr, 0); return i ? Math.round(rows.reduce((a, r) => a + r.pos * r.impr, 0) / i * 10) / 10 : 0; };

async function buildData(sa, { start, end }){
  const tok = await getToken(sa);
  const dailyStart = addDays(end, -27);
  const [dailyR, hourlyR, pageR, deviceR, queryR, qpR, totR, index] = await Promise.all([
    saQ(tok, ["date"], { start: dailyStart, end }),
    saQ(tok, ["HOUR"], { state: "HOURLY_ALL", start: end, end }),
    saQ(tok, ["page"], { start, end }),
    saQ(tok, ["device"], { start, end }),
    saQ(tok, ["query"], { start, end }),
    saQ(tok, ["query", "page"], { start, end }),
    saQ(tok, [], { start, end }),
    getIndex(tok),
  ]);
  const daily = dailyR.map(rf).map(d => ({ date: d.keys[0], impressions: d.impr, clicks: d.clicks, ctr: d.ctr, position: d.pos }));
  const hourly = hourlyR.map(r => ({ hour: r.keys[0], impressions: Math.round(r.impressions || 0), clicks: Math.round(r.clicks || 0) }));
  const device = deviceR.map(rf).map(r => ({ device: r.keys[0], impressions: r.impr, clicks: r.clicks, ctr: r.ctr }));
  const queries = queryR.map(rf).map(r => ({ q: r.keys[0], impressions: r.impr, clicks: r.clicks, position: r.pos, ctr: r.ctr })).sort((a, b) => b.impressions - a.impressions);
  const pages = pageR.map(rf);
  // per-geo by page path
  const gAgg = {}; GEOS.forEach(g => gAgg[g] = []);
  pages.forEach(r => { const g = geoOf(r.keys[0]); if (g) gAgg[g].push(r); });
  const geos = {};
  GEOS.forEach(g => { const rows = gAgg[g]; const impr = rows.reduce((a, r) => a + r.impr, 0); const clicks = rows.reduce((a, r) => a + r.clicks, 0);
    geos[g] = { impr, clicks, ctr: impr ? Math.round(clicks / impr * 10000) / 100 : 0, pos: wpos(rows) }; });
  const t = totR.length ? rf(totR[0]) : { impr: 0, clicks: 0, ctr: 0, pos: 0 };
  const totals = { impr: t.impr, clicks: t.clicks, ctr: t.ctr, pos: t.pos };
  const summary = { impressions: t.impr, clicks: t.clicks, ctr: t.ctr, position: t.pos, queries: queries.length, pages_seen: pages.filter(p => p.impr > 0).length };
  const brand = queries.filter(r => r.q.toLowerCase().includes("jetterix")).slice(0, 25);
  // striking-distance opportunities (position 3.5-20.5)
  const opportunities = queries.filter(r => r.position >= 3.5 && r.position <= 20.5 && r.impressions >= 3)
    .map(r => ({ q: r.q, impressions: r.impressions, clicks: r.clicks, position: r.position, ctr: r.ctr,
      potential: Math.round(r.impressions * (Math.max(0, 20 - r.position) / 20) * 10) / 10,
      hint: r.position <= 10 ? "Improve title/meta CTR" : "Push onto page 1" }))
    .sort((a, b) => b.potential - a.potential).slice(0, 25);
  // cannibalization
  const qm = {}; qpR.map(rf).forEach(r => { const q = r.keys[0]; (qm[q] = qm[q] || []).push({ page: r.keys[1], impressions: r.impr, position: r.pos }); });
  const cannibal = Object.entries(qm).filter(([, v]) => v.length > 1).map(([q, v]) => ({ q, pages: v.sort((a, b) => b.impressions - a.impressions) }))
    .sort((a, b) => b.pages.reduce((s, p) => s + p.impressions, 0) - a.pages.reduce((s, p) => s + p.impressions, 0)).slice(0, 12);
  // funnel from index coverage
  const funnel = { indexed: 0, crawled: 0, discovered: 0, unknown: 0 };
  index.forEach(i => { const c = (i.coverage || "").toLowerCase();
    if (c.includes("indexed") && !c.includes("not")) funnel.indexed++;
    else if (c.includes("crawled")) funnel.crawled++;
    else if (c.includes("discover")) funnel.discovered++; else funnel.unknown++; });
  const positions = queries.filter(r => r.position > 0).map(r => r.position);
  const best = positions.length ? Math.min(...positions) : 99;
  const milestones = { first_impression: t.impr > 0, first_click: t.clicks > 0, top10: best <= 10, top3: best <= 3, number1: best <= 1.5, best_position: best, indexed_pages: funnel.indexed, discovered_pages: funnel.discovered + funnel.crawled + funnel.indexed };
  return {
    generatedAt: new Date().toISOString().slice(0, 16).replace("T", " ") + " UTC", property: PROP, range: { start: ymd(start), end: ymd(end) },
    gsc: { connected: true, totals, geos }, summary, daily, hourly, device,
    queries: queries.slice(0, 40), brand, opportunities, cannibal, index, funnel, milestones, geoMeta: GEO_META,
  };
}

const DASH_URL = "https://buckgray6366.github.io/jx-dash/";
export default {
  async fetch(request, env){
    const cors = { "Access-Control-Allow-Origin": "*", "Cache-Control": "no-store", "Content-Type": "application/json" };
    if (request.method === "OPTIONS") return new Response(null, { headers: cors });
    if (request.method === "GET" && (request.headers.get("Accept") || "").includes("text/html")){
      const html = `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Jetterix · live data engine</title>
<style>body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:radial-gradient(900px 500px at 50% -10%,rgba(47,224,214,.18),transparent),#05171c;color:#eaf7f8;font:16px/1.6 system-ui,sans-serif}
.card{max-width:520px;text-align:center;padding:38px 34px;background:#0e2d36;border:1px solid #163b46;border-radius:18px}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;background:#19c6c0;box-shadow:0 0 12px #19c6c0;margin-right:7px;animation:p 1.6s infinite}@keyframes p{50%{opacity:.4}}
a.btn{display:inline-block;background:linear-gradient(90deg,#19c6c0,#fb5733);color:#04201f;font-weight:800;text-decoration:none;padding:13px 26px;border-radius:999px}</style></head>
<body><div class="card"><div><span class="dot"></span><b>Live data engine — online</b></div><h1>Data API, not the dashboard 🔌</h1>
<a class="btn" href="${DASH_URL}">Open the Jetterix dashboard →</a></div></body></html>`;
      return new Response(html, { headers: { "Content-Type": "text/html;charset=utf-8", "Access-Control-Allow-Origin": "*", "Cache-Control": "no-store" } });
    }
    try {
      const sa = JSON.parse(env.GSC_SA_JSON);
      const u = new URL(request.url);
      let start = u.searchParams.get("start"), end = u.searchParams.get("end");
      const re = /^\d{4}-\d{2}-\d{2}$/;
      if (!re.test(start || "") || !re.test(end || "")){ const t = new Date(); end = t.toISOString().slice(0, 10); start = new Date(t.getTime() - 6 * 86400000).toISOString().slice(0, 10); }
      return new Response(JSON.stringify(await buildData(sa, { start, end })), { headers: cors });
    } catch (e) { return new Response(JSON.stringify({ error: String(e) }), { status: 500, headers: cors }); }
  }
};
