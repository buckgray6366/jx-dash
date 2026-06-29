// jx-cron — Cloudflare scheduled Worker. Fires the GitHub refresh workflow on a reliable cron
// (GitHub's own scheduled cron is throttled/unreliable). Needs secret GH_PAT.
export default {
  async scheduled(event, env, ctx){
    ctx.waitUntil(fetch("https://api.github.com/repos/buckgray6366/jx-dash/actions/workflows/refresh.yml/dispatches", {
      method: "POST",
      headers: { "Authorization": "Bearer " + env.GH_PAT, "Accept": "application/vnd.github+json", "User-Agent": "jx-cron", "Content-Type": "application/json" },
      body: JSON.stringify({ ref: "main" }),
    }));
  },
  async fetch(req, env){
    // manual ping: hitting the URL also fires a refresh (handy for testing)
    const r = await fetch("https://api.github.com/repos/buckgray6366/jx-dash/actions/workflows/refresh.yml/dispatches", {
      method: "POST", headers: { "Authorization": "Bearer " + env.GH_PAT, "Accept": "application/vnd.github+json", "User-Agent": "jx-cron", "Content-Type": "application/json" }, body: JSON.stringify({ ref: "main" }),
    });
    return new Response("jx-cron: dispatched refresh -> GitHub " + r.status, { headers: { "content-type": "text/plain" } });
  }
};
