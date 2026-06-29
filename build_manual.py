#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate manual-backlinks.html — high-DA platforms the team posts by hand, with the article written + steps."""
import json, os, html
HERE = os.path.dirname(os.path.abspath(__file__))
FLAG = {"de":"🇩🇪","fr":"🇫🇷","en":"🇺🇸"}
def E(s): return html.escape(str(s), quote=True)

TASKS = [
 {"platform":"Medium","signup":"https://medium.com","write":"medium.com/new-story","lang":"en",
  "target":"https://tryjetterix.com/us/","anchor":"in-depth Jetterix review",
  "title":"I Tested the Jetterix Pressure Nozzle for a Month — My Honest Verdict",
  "body":"""I've wasted money on cheap hose attachments before, so I didn't expect much from the Jetterix high-pressure nozzle. A month of real use later, here's my honest verdict.

What it is
Jetterix is a metal nozzle that screws onto any standard garden hose. It narrows and concentrates your mains water into a far stronger jet — no electricity, no motor, no battery. You just attach it, turn the tap, and go.

How it performed
I used it on the driveway, the patio, garden furniture and the car. The jet is noticeably stronger than a normal spray gun, and it stripped off dirt and loose grime fast. Moss wedged between paving stones took a couple of passes and getting in close, but it came up. One honest caveat: the power depends heavily on your home's water pressure — low pressure means a weaker jet.

Who it's for
If you want to blast an entire industrial yard, you still need a real electric pressure washer. For the everyday jobs around a house, the nozzle is more than enough — and it stores in a drawer instead of a garage.

If you want the full breakdown, this in-depth Jetterix review covers the pros, the cons, real owner feedback and the current price.

My verdict: a clever, no-power tool that does what it promises — as long as you treat it as a nozzle upgrade, not a professional machine.""" },

 {"platform":"Blogger","signup":"https://www.blogger.com","write":"blogger.com → New Post","lang":"de",
  "target":"https://tryjetterix.com/de/","anchor":"ausführlichen Jetterix Erfahrungsbericht",
  "title":"Jetterix Erfahrungen: Mein ehrlicher Test der Hochdruckdüse",
  "body":"""Ich habe schon einige günstige Schlauchaufsätze ausprobiert und war jedes Mal enttäuscht. Deshalb war ich auch bei der Jetterix Hochdruckdüse skeptisch. Nach einem Monat im Einsatz ziehe ich ein ehrliches Fazit.

Was ist Jetterix?
Jetterix ist eine Düse, die man in Sekunden auf jeden Standard-Gartenschlauch schraubt. Sie bündelt den Wasserdruck der Leitung zu einem deutlich stärkeren Strahl — ganz ohne Strom, Motor oder Akku.

Meine Erfahrung im Alltag
Einfahrt, Terrasse, Gartenmöbel und Auto habe ich damit gereinigt. Der Strahl ist spürbar kräftiger als bei einer normalen Spritzpistole, und Schmutz löst sich erstaunlich gut. Bei festsitzendem Moos zwischen den Pflastersteinen muss man näher rangehen und zweimal drübergehen. Wichtig zu wissen: Die Leistung hängt stark vom Wasserdruck zu Hause ab.

Für wen lohnt es sich?
Wer einen ganzen Industriehof reinigen will, braucht weiterhin einen echten Hochdruckreiniger. Für die typischen Aufgaben rund ums Haus reicht die Düse locker — und sie passt in eine Schublade statt in die Garage.

Wer es genau wissen will, findet hier einen ausführlichen Jetterix Erfahrungsbericht mit Vor- und Nachteilen, echten Bewertungen und dem aktuellen Preis.

Mein Fazit: ein cleveres, stromloses Werkzeug, das hält was es verspricht — solange man weiß, dass es ein Düsenaufsatz und kein Profi-Gerät ist.""" },

 {"platform":"WordPress.com","signup":"https://wordpress.com/start","write":"WordPress → New Post","lang":"de",
  "target":"https://tryjetterix.com/de/","anchor":"kompletten Jetterix Test",
  "title":"Hochdruckdüse statt Hochdruckreiniger? Mein Jetterix Praxistest",
  "body":"""Ein elektrischer Hochdruckreiniger kostet schnell mehrere hundert Euro, braucht Stauraum und Wartung. Ich wollte wissen: Reicht für die meisten Hausbesitzer nicht auch eine gute Hochdruckdüse? Also habe ich die Jetterix Düse getestet.

Das Prinzip
Die Düse wird auf den Gartenschlauch geschraubt und nutzt den vorhandenen Leitungsdruck. Kein Kabel, kein Motor, kaum Platzbedarf. Aufschrauben, Wasser aufdrehen, fertig.

Der Praxistest
Terrasse, Zaun, Gartenmöbel und Auto ließen sich gut reinigen. An die Wucht eines 140-bar-Geräts kommt eine wassergetriebene Düse natürlich nicht heran — das ist klar und ehrlich gesagt. Für die regelmäßige Gartenpflege war die Leistung aber völlig ausreichend, und ich spare mir Anschaffung, Strom und Stellplatz.

Lohnt sich das?
Wer nur ein paar Mal pro Saison reinigt, fährt mit der Düse meiner Meinung nach besser als mit einem teuren Gerät, das die meiste Zeit ungenutzt herumsteht.

Eine gute Übersicht inklusive ehrlicher Nachteile bietet dieser kompletten Jetterix Test.

Fazit: für die typische Gartenpflege eine clevere, günstige und platzsparende Lösung.""" },

 {"platform":"Tumblr","signup":"https://www.tumblr.com/register","write":"Tumblr → New Text Post","lang":"fr",
  "target":"https://tryjetterix.com/fr/","anchor":"avis détaillé sur Jetterix",
  "title":"Jetterix avis : mon test honnête de la buse haute pression",
  "body":"""J'avais déjà acheté plusieurs embouts de tuyau bon marché, sans résultat. La buse haute pression Jetterix m'a donc laissé sceptique au départ. Après un mois d'utilisation, voici mon avis honnête.

Le principe
Jetterix se visse sur n'importe quel tuyau d'arrosage standard et concentre la pression de l'eau en un jet bien plus puissant — sans électricité ni moteur. On la fixe, on ouvre le robinet, et c'est parti.

Mon retour d'expérience
J'ai nettoyé l'allée, la terrasse, le mobilier de jardin et la voiture. Le jet est nettement plus fort qu'un pistolet d'arrosage classique. Pour la mousse incrustée entre les pavés, il faut s'approcher et repasser une fois. À savoir : la puissance dépend de la pression de votre réseau d'eau.

Pour qui ?
Pour nettoyer une grande surface industrielle, un vrai nettoyeur électrique reste nécessaire. Pour les tâches courantes autour de la maison, la buse suffit largement — et elle se range dans un tiroir.

Pour ceux qui veulent les détails, voici un avis détaillé sur Jetterix avec les avantages, les limites et le prix du jour.

Mon verdict : un accessoire malin et sans électricité, à condition de ne pas en attendre les performances d'un nettoyeur professionnel.""" },

 {"platform":"Substack","signup":"https://substack.com","write":"Substack → New post","lang":"fr",
  "target":"https://tryjetterix.com/fr/","anchor":"test complet de la buse Jetterix",
  "title":"J'ai testé la buse Jetterix pendant un mois — voici mon verdict",
  "body":"""Chaque printemps, ma terrasse verdit et l'allée se salit. Je ne voulais pas investir dans un nettoyeur haute pression électrique, lourd et encombrant. J'ai donc testé la buse Jetterix pendant un mois.

Comment ça marche
La buse se visse sur le tuyau d'arrosage et concentre la pression de l'eau en un jet puissant. Aucun câble, aucun moteur, aucune consommation électrique. On visse, on ouvre l'eau, et c'est tout.

À l'usage
Bois de la terrasse, clôture, voiture et mobilier se rincent facilement. Le jet est bien plus fort qu'avec un pistolet classique. Pour la saleté très incrustée, il faut un peu de patience et insister. La performance dépend de la pression de votre eau.

Le bon choix ?
Pour un usage occasionnel et l'entretien courant, la buse est, à mon avis, plus pratique qu'un appareil coûteux qui prend de la place et reste inutilisé la plupart du temps.

J'avais lu un test complet de la buse Jetterix avant de commander, ce qui m'a aidée à décider en connaissant aussi les limites.

Au final : un bon rapport qualité-prix, abordable, facile à ranger et sans électricité.""" },
]

cards = []
for i, t in enumerate(TASKS, 1):
    bid = "b%d" % i
    cards.append(f'''<div class="task">
  <div class="th"><h2>{i} · {E(t['platform'])} <span class="fl">{FLAG[t['lang']]} {t['lang'].upper()}</span></h2>
    <a class="go" href="{E(t['signup'])}" target="_blank">sign up ↗</a></div>
  <ol class="steps">
    <li>Create a free account at <a href="{E(t['signup'])}" target="_blank">{E(t['signup'].split('//')[1])}</a> and start a new post ({E(t['write'])}).</li>
    <li>Copy the <b>Title</b> and <b>Article</b> below into the post.</li>
    <li>In the post, select the words <b>“{E(t['anchor'])}”</b>, click the link button, and paste this URL: <code>{E(t['target'])}</code></li>
    <li>Publish. Copy the live post URL and send it to me — I add it to the Backlinks tracker.</li>
  </ol>
  <div class="fld"><div class="fh"><label>Title</label><button class="cp" data-t="t{i}">Copy title</button></div><div class="v" id="t{i}">{E(t['title'])}</div></div>
  <div class="fld"><div class="fh"><label>Article</label><button class="cp" data-t="{bid}">Copy article</button></div><pre class="v body" id="{bid}">{E(t['body'])}</pre></div>
  <div class="link">🔗 Link the words <b>“{E(t['anchor'])}”</b> → <code>{E(t['target'])}</code></div>
</div>''')

PAGE = f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow">
<meta http-equiv="Cache-Control" content="no-cache, must-revalidate"><title>Jetterix — Manual backlinks</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=Inter:wght@400;500;600;700;800&display=swap">
<style>
:root{{--bg:#05171c;--card:#0e2d36;--line:#163b46;--ink:#eaf7f8;--mut:#88aab1;--teal:#19c6c0;--aqua:#2fe0d6;--coral:#fb5733;--good:#26d07c;--head:"Bricolage Grotesque",system-ui,sans-serif;--body:"Inter",system-ui,sans-serif}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(900px 480px at 82% -8%,#0c343d,transparent),var(--bg);color:var(--ink);font:15px/1.55 var(--body)}}
.wrap{{max-width:860px;margin:0 auto;padding:24px 18px 70px}}
h1{{font-family:var(--head);letter-spacing:-.02em;margin:0;font-size:24px;display:flex;align-items:center;gap:11px}}
.drop{{width:16px;height:20px;border-radius:50% 50% 50% 0;transform:rotate(45deg);background:linear-gradient(135deg,var(--aqua),#0a96ac);box-shadow:0 0 14px rgba(47,224,214,.4)}}
.tag{{font-family:var(--body);font-weight:700;font-size:10px;color:var(--coral);border:1px solid var(--line);padding:3px 9px;border-radius:7px;letter-spacing:.1em}}
.sub{{color:var(--mut);font-size:13px;margin:6px 0 20px}}
a{{color:var(--aqua);text-decoration:none;font-weight:600}}
.topbar{{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}}.back{{font-size:13px}}
.menu{{position:relative}}.menu-btn{{font:inherit;font-size:12.5px;font-weight:800;color:#04201f;background:linear-gradient(180deg,var(--aqua),var(--teal));border:0;border-radius:999px;padding:6px 13px;cursor:pointer}}
.menu-list{{position:absolute;right:0;top:36px;background:var(--card);border:1px solid var(--line);border-radius:12px;box-shadow:0 14px 34px rgba(0,0,0,.45);list-style:none;margin:0;padding:6px;min-width:215px;display:none;z-index:80}}
.menu.open .menu-list{{display:block}}.menu-list li a{{display:block;padding:9px 11px;border-radius:9px;color:var(--ink);font-size:13.5px;font-weight:600}}.menu-list li a:hover{{background:var(--bg)}}.menu-list li a.cur{{color:var(--aqua)}}
.task{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px 20px;margin-bottom:18px}}
.th{{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:10px}}
.th h2{{font-family:var(--head);font-size:18px;margin:0;display:flex;align-items:center;gap:9px}}
.th .fl{{font-family:var(--body);font-size:11px;font-weight:700;color:var(--mut);border:1px solid var(--line);padding:2px 8px;border-radius:6px}}
.go{{font-size:12.5px}}
.steps{{margin:0 0 14px;padding-left:20px;font-size:13.5px}} .steps li{{padding:3px 0;color:#d6ebed}} .steps b{{color:#fff}}
.steps code,.link code{{background:#05171c;border:1px solid var(--line);padding:1px 6px;border-radius:5px;color:var(--aqua);font-size:12px;word-break:break-all}}
.fld{{margin:10px 0}}.fh{{display:flex;justify-content:space-between;align-items:center;margin-bottom:5px}}
label{{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--mut);font-weight:700}}
.cp{{background:var(--teal);color:#04201f;border:0;border-radius:7px;padding:5px 12px;font-weight:800;font-size:11.5px;cursor:pointer;font-family:var(--body)}}.cp.done{{background:var(--good)}}
.v{{background:#05171c;border:1px solid var(--line);border-radius:9px;padding:11px 13px;font-size:13.5px;color:#e7f4f5}}
.body{{white-space:pre-wrap;font-family:var(--body);line-height:1.6;max-height:230px;overflow:auto;margin:0}}
.link{{background:linear-gradient(90deg,rgba(47,224,214,.12),transparent);border:1px solid var(--line);border-left:4px solid var(--teal);border-radius:9px;padding:9px 13px;font-size:13px;margin-top:10px}}
.foot{{color:var(--mut);font-size:11.5px;text-align:center;margin-top:18px}}
</style></head><body><div class="wrap">
<div class="topbar"><a class="back" href="./">← Back to dashboard</a>
  <div class="menu" id="menu"><button class="menu-btn" id="menuBtn">☰ Menu</button>
  <ul class="menu-list"><li><a href="./">📊 Dashboard</a></li><li><a href="change-links.html">⚙️ Change affiliate links</a></li><li><a href="backlinks.html">🔗 Backlinks</a></li><li><a href="manual-backlinks.html" class="cur">📝 Manual backlinks</a></li><li><a href="https://buckgray6366.github.io/jx-playbook/" target="_blank">📋 Playbook ↗</a></li></ul></div>
</div>
<h1><span class="drop"></span>Manual backlinks <span class="tag">TEAM · HIGH-DA</span></h1>
<div class="sub">5 high-authority platforms that block automated signup — post these by hand. The article is written; copy, paste, add the one link, publish, send me the URL.</div>
{''.join(cards)}
<div class="foot">Confidential · internal · send each published URL back to add it to the Backlinks tracker</div>
<script>
document.getElementById("menuBtn").addEventListener("click",function(e){{e.stopPropagation();document.getElementById("menu").classList.toggle("open");}});
document.addEventListener("click",function(){{document.getElementById("menu").classList.remove("open");}});
document.querySelectorAll(".cp").forEach(function(b){{b.addEventListener("click",function(){{
  var txt=document.getElementById(this.dataset.t).innerText,self=this;
  var done=function(){{self.textContent="✓ Copied";self.classList.add("done");setTimeout(function(){{self.textContent=self.dataset.t[0]==="t"?"Copy title":"Copy article";self.classList.remove("done");}},1500);}};
  if(navigator.clipboard&&navigator.clipboard.writeText){{navigator.clipboard.writeText(txt).then(done).catch(function(){{fb(txt,done);}});}}else fb(txt,done);
}});}});
function fb(txt,done){{var t=document.createElement("textarea");t.value=txt;t.style.position="fixed";t.style.opacity="0";document.body.appendChild(t);t.select();try{{document.execCommand("copy");done();}}catch(e){{}}document.body.removeChild(t);}}
</script>
</body></html>'''
open(os.path.join(HERE,"manual-backlinks.html"),"w",encoding="utf-8").write(PAGE)
print("manual-backlinks.html written:", len(TASKS), "platforms")
