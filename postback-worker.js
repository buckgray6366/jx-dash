// Jetterix postback receiver — OasisAds (or any network) pings this on click/conversion.
// Persists events to buckgray6366/jx-dash/postback.json via GitHub API (no KV needed).
// GET /pb?type=conversion&sub2=jx-de&payout=55&txid=ABC   -> records a conversion
// GET /data  -> aggregated per-geo {clicks,conv,revenue} for the dashboard (CORS *)
const REPO = "buckgray6366/jx-dash", FILE = "postback.json";
const GH = "https://api.github.com/repos/" + REPO + "/contents/" + FILE;
const num = v => { const n = parseFloat(v); return isFinite(n) ? n : 0; };
function geoOf(sub){ sub = String(sub || "").toLowerCase(); const m = sub.match(/jx[-_]?([a-z]{2})/); return m ? m[1] : (["us","uk","au","de","fr"].includes(sub) ? sub : "??"); }

async function ghGet(pat){
  const r = await fetch(GH, { headers: { Authorization: "Bearer " + pat, "User-Agent": "jx-postback", Accept: "application/vnd.github+json" } });
  if (r.status === 404) return { events: [], sha: null };
  const j = await r.json();
  try { return { ...JSON.parse(decodeURIComponent(escape(atob(j.content.replace(/\n/g, ""))))), sha: j.sha }; }
  catch (e) { return { events: [], sha: j.sha || null }; }
}
async function ghPut(pat, obj, sha){
  const body = { message: "postback", content: btoa(unescape(encodeURIComponent(JSON.stringify({ events: obj.events }, null, 0)))), sha: sha || undefined };
  const r = await fetch(GH, { method: "PUT", headers: { Authorization: "Bearer " + pat, "User-Agent": "jx-postback", Accept: "application/vnd.github+json", "Content-Type": "application/json" }, body: JSON.stringify(body) });
  return r.ok;
}
function aggregate(events){
  const geos = {}; ["us","uk","au","de","fr"].forEach(g => geos[g] = { clicks: 0, conv: 0, revenue: 0 });
  (events || []).forEach(e => { const g = e.geo; if (!geos[g]) geos[g] = { clicks: 0, conv: 0, revenue: 0 };
    if (e.type === "click") geos[g].clicks++; else { geos[g].conv++; geos[g].revenue += num(e.payout); } });
  const tot = Object.values(geos).reduce((a, v) => ({ clicks: a.clicks + v.clicks, conv: a.conv + v.conv, revenue: a.revenue + v.revenue }), { clicks: 0, conv: 0, revenue: 0 });
  return { connected: true, geos, totals: tot, count: (events || []).length, note: "" };
}

export default {
  async fetch(req, env){
    const u = new URL(req.url), cors = { "Access-Control-Allow-Origin": "*", "Cache-Control": "no-store", "Content-Type": "application/json" };
    if (req.method === "OPTIONS") return new Response(null, { headers: cors });
    const pat = env.GH_PAT;
    try {
      if (u.pathname.endsWith("/data")){
        const st = await ghGet(pat); return new Response(JSON.stringify(aggregate(st.events)), { headers: cors });
      }
      // record a postback (accept many param name variants)
      const q = u.searchParams, g = q.get.bind(q);
      const sub = g("sub2") || g("aff_sub2") || g("s2") || g("subid2") || g("sub_id2") || g("aff_sub");
      const type = (g("type") || g("status") || "conversion").toLowerCase().includes("click") ? "click" : "conversion";
      const ev = { ts: new Date().toISOString(), geo: geoOf(sub), sub: sub || "", type,
                   payout: num(g("payout") || g("sum") || g("amount") || g("revenue") || g("payout_amount")),
                   txid: g("txid") || g("transaction_id") || g("tid") || g("click_id") || "" };
      if (!pat) return new Response(JSON.stringify({ ok: false, error: "no GH_PAT" }), { status: 500, headers: cors });
      let st = await ghGet(pat); st.events = (st.events || []).concat(ev);
      let ok = await ghPut(pat, st, st.sha);
      if (!ok) { st = await ghGet(pat); st.events = (st.events || []).concat(ev); ok = await ghPut(pat, st, st.sha); } // retry on sha conflict
      // respond with a 1x1 gif so it works as a pixel too
      return new Response(JSON.stringify({ ok, recorded: ev }), { headers: cors });
    } catch (e) { return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500, headers: cors }); }
  }
};
