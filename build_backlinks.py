#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate backlinks.html from backlinks.json (screenshots in bl/). Re-run after adding links."""
import json, os, html, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
arts = json.load(open(os.path.join(HERE, "backlinks.json")))
FLAG = {"de": "🇩🇪", "fr": "🇫🇷", "en": "🇺🇸", "uk": "🇬🇧", "au": "🇦🇺"}
def E(s): return html.escape(str(s), quote=True)
by = {}
for a in arts: by[a["lang"]] = by.get(a["lang"], 0) + 1
summ = " · ".join("%s %d" % (FLAG.get(k, k.upper()), v) for k, v in sorted(by.items()))
cards = []
for a in arts:
    tgt = a["target"].replace("https://tryjetterix.com", "") or "/"
    shot = a.get("shot", "")
    st = '<span class="ok">✓ live</span>' if a.get("verified") else '<span class="pend">pending</span>'
    cards.append(f'''<div class="bl">
  <a class="thumb" href="{E(a['url'])}" target="_blank">{f'<img src="{E(shot)}" alt="" loading="lazy">' if shot else ''}</a>
  <div class="meta">
    <div class="t"><a href="{E(a['url'])}" target="_blank">{E(a['title'])}</a></div>
    <div class="r">{FLAG.get(a['lang'],a['lang'])} {E(a['lang'].upper())} · {E(a['platform'])} · {st}</div>
    <div class="r">anchor: <b>“{E(a['anchor'])}”</b> → <code>{E(tgt)}</code></div>
    <a class="open" href="{E(a['url'])}" target="_blank">open article ↗</a>
  </div>
</div>''')
PAGE = f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow">
<meta http-equiv="Cache-Control" content="no-cache, must-revalidate"><title>Jetterix — Backlinks</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=Inter:wght@400;500;600;700;800&display=swap">
<style>
:root{{--bg:#05171c;--card:#0e2d36;--line:#163b46;--ink:#eaf7f8;--mut:#88aab1;--teal:#19c6c0;--aqua:#2fe0d6;--coral:#fb5733;--good:#26d07c;--warn:#ffb02e;--head:"Bricolage Grotesque",system-ui,sans-serif;--body:"Inter",system-ui,sans-serif}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(900px 480px at 82% -8%,#0c343d,transparent),var(--bg);color:var(--ink);font:15px/1.5 var(--body)}}
.wrap{{max-width:980px;margin:0 auto;padding:24px 18px 70px}}
h1{{font-family:var(--head);letter-spacing:-.02em;margin:0;font-size:24px;display:flex;align-items:center;gap:11px}}
.drop{{width:16px;height:20px;border-radius:50% 50% 50% 0;transform:rotate(45deg);background:linear-gradient(135deg,var(--aqua),#0a96ac);box-shadow:0 0 14px rgba(47,224,214,.4)}}
.tag{{font-family:var(--body);font-weight:700;font-size:10px;color:var(--coral);border:1px solid var(--line);padding:3px 9px;border-radius:7px;letter-spacing:.1em}}
.sub{{color:var(--mut);font-size:13px;margin:6px 0 20px}}
a{{color:var(--aqua);text-decoration:none}}
.topbar{{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}}
.back{{font-size:13px}}
.menu{{position:relative}}.menu-btn{{font:inherit;font-size:12.5px;font-weight:800;color:#04201f;background:linear-gradient(180deg,var(--aqua),var(--teal));border:0;border-radius:999px;padding:6px 13px;cursor:pointer}}
.menu-list{{position:absolute;right:0;top:36px;background:var(--card);border:1px solid var(--line);border-radius:12px;box-shadow:0 14px 34px rgba(0,0,0,.45);list-style:none;margin:0;padding:6px;min-width:215px;display:none;z-index:80}}
.menu.open .menu-list{{display:block}}.menu-list li a{{display:block;padding:9px 11px;border-radius:9px;color:var(--ink);font-size:13.5px;font-weight:600}}.menu-list li a:hover{{background:var(--bg)}}.menu-list li a.cur{{color:var(--aqua)}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.bl{{background:var(--card);border:1px solid var(--line);border-radius:16px;overflow:hidden;display:flex;flex-direction:column}}
.bl .thumb{{display:block;height:170px;overflow:hidden;background:#fff;border-bottom:1px solid var(--line)}}
.bl .thumb img{{width:100%;display:block}}
.bl .meta{{padding:13px 15px}}
.bl .t{{font-family:var(--head);font-weight:700;font-size:14.5px;line-height:1.3;margin-bottom:7px}}
.bl .t a{{color:var(--ink)}} .bl .t a:hover{{color:var(--aqua)}}
.bl .r{{font-size:12px;color:var(--mut);margin:3px 0}}
.bl .r b{{color:#dfeff0;font-weight:600}} .bl code{{background:#05171c;border:1px solid var(--line);padding:1px 6px;border-radius:5px;color:var(--aqua);font-size:11.5px}}
.ok{{color:var(--good);font-weight:700}} .pend{{color:var(--warn);font-weight:700}}
.open{{display:inline-block;margin-top:8px;font-size:12.5px;font-weight:700}}
.foot{{color:var(--mut);font-size:11.5px;text-align:center;margin-top:20px}}
@media(max-width:720px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body><div class="wrap">
<div class="topbar"><a class="back" href="./">← Back to dashboard</a>
  <div class="menu" id="menu"><button class="menu-btn" id="menuBtn">☰ Menu</button>
  <ul class="menu-list"><li><a href="./">📊 Dashboard</a></li><li><a href="change-links.html">⚙️ Change affiliate links</a></li><li><a href="backlinks.html" class="cur">🔗 Backlinks</a></li><li><a href="manual-backlinks.html">📝 Manual backlinks</a></li><li><a href="https://buckgray6366.github.io/jx-playbook/" target="_blank">📋 Playbook ↗</a></li></ul></div>
</div>
<h1><span class="drop"></span>Backlinks <span class="tag">LINK BUILDING</span></h1>
<div class="sub">{len(arts)} live · {summ} · native articles, each links once deep with a native anchor · click a card to open the article</div>
<div class="grid">
{''.join(cards)}
</div>
<div class="foot">Updated {datetime.date.today().isoformat()} · screenshots are live captures · confidential / internal</div>
<script>document.getElementById("menuBtn").addEventListener("click",function(e){{e.stopPropagation();document.getElementById("menu").classList.toggle("open");}});document.addEventListener("click",function(){{document.getElementById("menu").classList.remove("open");}});</script>
</body></html>'''
open(os.path.join(HERE, "backlinks.html"), "w", encoding="utf-8").write(PAGE)
print("backlinks.html written:", len(arts), "articles")
