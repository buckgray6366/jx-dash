#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Jetterix dashboard — OasisAds (awareads/Kalipso) reporting pull via Gonzo residential proxy.
The panel API blocks datacenter IPs (serves SPA HTML); a residential exit returns real JSON.
Auth -> /report/campaign (one row per geo offer) + /report-total/campaign (account totals) -> data.json.
Run: python3 pull_oasis.py   (local: key files; CI: env GONZO_KEY / OASIS_USER / OASIS_PASS)."""
import json, os, datetime, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
GONZO_KEY = os.environ.get("GONZO_KEY") or open("/root/.config/gonzo/key").read().strip()
OASIS_USER = os.environ.get("OASIS_USER", "contact@gcalit.org")
OASIS_PASS = os.environ.get("OASIS_PASS", "Qwer1234@")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
BASE = "https://publishers.oasisads.com/api/1"
OFFER_GEO = {"O6887": "us", "O6888": "uk", "O6889": "au", "O6790": "de", "O6791": "fr"}

def gonzo_proxy():
    body = json.dumps({"country": "US", "ttl": 30, "ttl_unit": "m", "format": "ip:port:user:pass"}).encode()
    r = urllib.request.Request("https://api.gonzoproxy.app/functions/v1/proxy-api/generate", data=body,
                               headers={"x-api-key": GONZO_KEY, "Content-Type": "application/json"})
    px = json.load(urllib.request.urlopen(r, timeout=30))["proxies"][0]
    host, port, user, pwd = px.split(":")
    return "http://%s:%s@%s:%s" % (user, pwd, host, port)

def make_opener(proxy):
    return urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))

def post(opener, path, body, token=None):
    h = {"User-Agent": UA, "Accept": "application/json", "Content-Type": "application/json",
         "Origin": "https://publishers.oasisads.com", "Referer": "https://publishers.oasisads.com/"}
    if token: h["Authorization"] = "Bearer " + token
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(), method="POST", headers=h)
    return json.load(opener.open(req, timeout=50))

def main():
    proxy = gonzo_proxy()
    op = make_opener(proxy)
    token = post(op, "/user/authenticate", {"user_name": OASIS_USER, "password": OASIS_PASS})["result"]["data"]["jwt"]
    end = datetime.date.today(); start = end - datetime.timedelta(days=90)
    dr = {"date_range": {"start": str(start), "end": str(end)}}
    rep = post(op, "/report/campaign", {"filters": {"offer_id": None, **dr}, "limit": 50, "sort": "campaign_id", "order": 1}, token)
    rows = (rep.get("result") or {}).get("data") or []
    tot = post(op, "/report-total/campaign", {"filters": {"offer_id": None, **dr}, "limit": 50, "sort": "campaign_id", "order": 1}, token)
    trow = ((tot.get("result") or {}).get("data") or [{}])[0]

    geos = {g: {"clicks": 0, "conv": 0, "revenue": 0.0, "partials": 0} for g in OFFER_GEO.values()}
    for r in rows:
        g = OFFER_GEO.get(r.get("offer_id"))
        if not g: continue
        geos[g] = {"clicks": int(r.get("clicks", 0)), "conv": int(r.get("conversions", 0)),
                   "revenue": float(r.get("earnings", 0) or 0), "partials": int(r.get("partials", 0))}

    path = os.path.join(HERE, "data.json"); data = json.load(open(path))
    data["oasis"]["geos"] = {g: {"clicks": v["clicks"], "conv": v["conv"], "revenue": v["revenue"]} for g, v in geos.items()}
    data["oasis"]["connected"] = True
    data["oasis"]["partials"] = {g: v["partials"] for g, v in geos.items()}
    # OUR totals = sum of the 5 Jetterix geo-offers (account total also includes the publisher's other offers)
    data["oasis"]["totals"] = {"clicks": sum(v["clicks"] for v in geos.values()), "conv": sum(v["conv"] for v in geos.values()),
                               "partials": sum(v["partials"] for v in geos.values()), "revenue": round(sum(v["revenue"] for v in geos.values()), 2)}
    data["oasis"]["account_total"] = {"clicks": int(trow.get("clicks", 0)), "conv": int(trow.get("conversions", 0)),
                                       "partials": int(trow.get("partials", 0)), "revenue": float(trow.get("earnings", 0) or 0)}
    data["oasis"]["note"] = "Live from OasisAds reporting (residential pull). 'partials' = checkout-started, not yet paid."
    data["updated"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    json.dump(data, open(path, "w"), ensure_ascii=False, indent=2)
    print("OasisAds pull OK — totals:", data["oasis"]["totals"], "| per-geo clicks:",
          {g: data["oasis"]["geos"][g]["clicks"] for g in OFFER_GEO.values()})

if __name__ == "__main__":
    main()
