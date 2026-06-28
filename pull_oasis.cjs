/* Jetterix dashboard — OasisAds (Kalipso panel) stealth pull.
 * The panel (publishers.oasisads.com) is bot-protected: /api/1/* returns an HTML challenge
 * to datacenter/headless requests. So this runs Playwright with a real-browser fingerprint and,
 * when provided, a residential proxy (env OASIS_PROXY=http://user:pass@host:port).
 *
 * Per-geo isolation = our subid s2 = jx-<geo>. Writes the oasis.* section of data.json.
 * Run: OASIS_PROXY=... node pull_oasis.cjs
 * No data yet (new offer) — this returns zeros until clicks start; safe to run anytime.
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const USER = process.env.OASIS_USER || 'contact@gcalit.org';
const PASS = process.env.OASIS_PASS || 'Qwer1234@';
const PROXY = process.env.OASIS_PROXY || null;
const GEOS = ['us', 'uk', 'au', 'de', 'fr'];
const DATA = path.join(__dirname, 'data.json');

(async () => {
  const launch = { headless: true };
  if (PROXY) launch.proxy = { server: PROXY };
  const b = await chromium.launch(launch);
  const ctx = await b.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    viewport: { width: 1440, height: 1000 }, locale: 'en-US', timezoneId: 'America/New_York',
  });
  // light stealth: hide webdriver
  await ctx.addInitScript(() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }); });
  const p = await ctx.newPage();
  let token = null, authJson = null;
  p.on('response', async r => {
    if (/\/api\/1\/user\/authenticate/.test(r.url())) {
      try { authJson = await r.json(); } catch (e) {}
    }
  });

  const result = { ok: false, blocked: false, geos: {} };
  GEOS.forEach(g => result.geos[g] = { clicks: 0, conv: 0, revenue: 0 });
  try {
    await p.goto('https://publishers.oasisads.com/login', { waitUntil: 'networkidle', timeout: 45000 });
    await p.fill('input[name=user_name]', USER);
    await p.fill('input[name=password]', PASS);
    await p.press('input[name=password]', 'Enter').catch(() => {});
    await p.waitForTimeout(6000);

    if (!authJson || typeof authJson !== 'object') {
      result.blocked = true;
      console.log('LOGIN BLOCKED: /api/1/user/authenticate did not return JSON (bot wall). ' +
                  (PROXY ? 'Proxy in use but still blocked.' : 'Set OASIS_PROXY=<residential proxy> and retry.'));
    } else {
      token = authJson.token || authJson.access_token || (authJson.data && authJson.data.token) || null;
      result.ok = !!token;
      // NOTE: once login succeeds, query the panel's stats endpoint here and bucket by subid jx-<geo>.
      // Endpoint shape to confirm on first successful auth (e.g. /api/1/report/statistics?group_by=sub2).
      console.log('LOGIN OK token=' + (token ? token.slice(0, 12) + '…' : 'none') +
                  ' — TODO: wire stats endpoint (no data yet, new offer).');
    }
  } catch (e) {
    console.log('ERROR:', e.message);
  }
  await b.close();

  // write back (only flips connected=true when we actually got authenticated data)
  const data = JSON.parse(fs.readFileSync(DATA, 'utf8'));
  if (result.ok) {
    data.oasis.geos = result.geos;
    data.oasis.connected = true;
    data.oasis.note = '';
  } else {
    data.oasis.connected = false;
    data.oasis.note = result.blocked
      ? 'OasisAds panel blocked automation — needs a residential proxy (OASIS_PROXY). No data yet (new offer).'
      : 'OasisAds pull pending — no data yet (new offer).';
  }
  data.updated = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
  fs.writeFileSync(DATA, JSON.stringify(data, null, 2));
  console.log('data.json updated (oasis.connected=' + data.oasis.connected + ')');
})();
