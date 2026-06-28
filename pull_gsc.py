#!/root/.config/gsc/venv/bin/python
# -*- coding: utf-8 -*-
"""Jetterix dashboard — Google Search Console pull. Splits metrics by geo via page path.
Run: python3 pull_gsc.py   (writes the gsc.* section of data.json in place)
CI: set GSC_SA_JSON secret; local: uses /root/.config/gsc/sa.json.
Activates once tryjetterix.com is verified + the service account is added as a user."""
import json, os, datetime, time
from google.oauth2 import service_account
import google.auth.transport.requests as gr
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = "/root/.config/gsc/sa.json"
PROP_ENC = "sc-domain%3Atryjetterix.com"
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
SA_URL = f"https://www.googleapis.com/webmasters/v3/sites/{PROP_ENC}/searchAnalytics/query"
GEOS = ["us", "uk", "au", "de", "fr"]

def auth():
    info = os.environ.get("GSC_SA_JSON")
    c = (service_account.Credentials.from_service_account_info(json.loads(info), scopes=SCOPES)
         if info else service_account.Credentials.from_service_account_file(KEY, scopes=SCOPES))
    c.refresh(gr.Request())
    return c.token

def query(token, days=7):
    end = datetime.date.today()
    body = {"startDate": str(end - datetime.timedelta(days=days)), "endDate": str(end),
            "dimensions": ["page"], "rowLimit": 1000, "dataState": "all"}
    for attempt in range(3):
        try:
            r = requests.post(SA_URL, headers={"Authorization": "Bearer " + token,
                              "Content-Type": "application/json"}, json=body, timeout=30)
            if r.status_code == 200:
                return r.json().get("rows", []), None
            if r.status_code in (429, 500, 503):
                time.sleep(2 + attempt * 2); continue
            return [], f"HTTP {r.status_code}: {r.text[:160]}"
        except Exception as e:
            time.sleep(2); err = str(e)
    return [], err

def geo_of(url):
    for g in GEOS:
        if f"/{g}/" in url:
            return g
    return None

def main():
    path = os.path.join(HERE, "data.json")
    data = json.load(open(path))
    try:
        token = auth()
    except Exception as e:
        print("GSC auth failed (property/SA not connected yet):", e)
        return
    rows, err = query(token)
    if err:
        print("GSC query error:", err); return
    agg = {g: {"impr": 0, "clicks": 0, "pos_w": 0.0} for g in GEOS}
    for r in rows:
        g = geo_of((r.get("keys") or [""])[0])
        if not g: continue
        impr = int(r.get("impressions", 0))
        agg[g]["impr"] += impr
        agg[g]["clicks"] += int(r.get("clicks", 0))
        agg[g]["pos_w"] += float(r.get("position", 0)) * impr
    out = {}
    for g in GEOS:
        a = agg[g]; impr = a["impr"]
        out[g] = {"impr": impr, "clicks": a["clicks"],
                  "ctr": round(a["clicks"] / impr * 100, 2) if impr else 0,
                  "pos": round(a["pos_w"] / impr, 1) if impr else 0}
    data["gsc"]["geos"] = out
    data["gsc"]["connected"] = True
    data["gsc"]["note"] = ""
    data["updated"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    json.dump(data, open(path, "w"), ensure_ascii=False, indent=2)
    print("GSC pull OK:", {g: out[g]["impr"] for g in GEOS}, "impressions")

if __name__ == "__main__":
    main()
