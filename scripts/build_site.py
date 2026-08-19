#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import argparse, json, shutil, html

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/"data"
DOMAIN = "https://otasports.info"

def esc(x): return html.escape(str(x), quote=True)
def load_markets(): return json.loads((DATA/"markets.json").read_text(encoding="utf-8"))
def load_daily(slug, ds):
    p=DATA/"daily"/slug/f"{ds}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
def all_daily(slug):
    d=DATA/"daily"/slug
    if not d.exists(): return []
    return sorted((json.loads(p.read_text(encoding="utf-8")) for p in d.glob("????-??-??.json")), key=lambda x:x["date"])
def fmt(ds): return datetime.strptime(ds,"%Y-%m-%d").strftime("%A, %B %-d, %Y")
def short(ds): return datetime.strptime(ds,"%Y-%m-%d").strftime("%b. %-d, %Y")
def plural(n,noun="listing"): return f"{n} {noun}" if n==1 else f"{n} {noun}s"

def head(title,desc,canonical,depth,robots="index,follow,max-image-preview:large"):
    p="../"*depth
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}"><link rel="canonical" href="{canonical}">
<link rel="stylesheet" href="{p}assets/site.css"></head><body>
<input aria-label="Use dark mode" class="theme-switch" id="theme-switch" type="checkbox"><div class="site">'''

def header(depth,m=None):
    p="../"*depth
    if m:
        s=m["slug"]
        nav=f'<a href="{p}">All markets</a><a href="{p}{s}/sports-on-tv-today/">Today</a><a href="{p}{s}/sports-on-tv-tomorrow/">Tomorrow</a><a href="{p}{s}/archive/">Archive</a>'
    else:
        nav='<a href="#markets">Markets</a>'
    return f'''<header><div class="wrap"><div class="brandbar"><div class="brand">
<div class="brand-name"><a href="{p}">OTA SPORTS</a></div><small>Free antenna sports, market by market.</small></div>
<label class="theme-toggle" for="theme-switch"><span class="night">Night mode</span><span class="day">Day mode</span></label>
</div><nav>{nav}</nav></div></header>'''

def footer():
    return '<footer><div class="wrap">Over-the-air sports programming only. All times are local to the television market. Advance schedules can change; low-power reception varies by location.</div></footer></div></body></html>'

def listing(d,missing=None):
    if d is None:
        return f'<section class="section"><h2>Listings</h2><div class="notice"><strong>{esc(missing or "Listings have not been published for this date.")}</strong></div></section>'
    ev=d.get("events",[])
    if not ev:
        note=d.get("scan_note","No verified OTA sports programming found for this date.")
        return f'<section class="section"><h2>Listings</h2><div class="notice"><strong>No verified OTA sports programming found for this date.</strong><span>{esc(note)}</span></div></section>'
    rows=[]
    for e in ev:
        tim=e["start"]+(f'–{e["end"]}' if e.get("end") else "")
        cls=" live" if e.get("status","").startswith("LIVE") else ""
        rows.append(f'''<div class="row"><div class="time">{esc(tim)}</div><div>
<div class="status{cls}">{esc(e.get("status",""))} · {esc(e.get("sport","").upper())}</div>
<h3>{esc(e.get("event",""))}</h3><p>{esc(e.get("detail",""))}</p></div>
<div class="ch">{esc(e.get("station",""))}<br><span class="network">{esc(e.get("network",""))}</span></div></div>''')
    return '<section class="section"><h2>Listings</h2><div class="listing">'+"".join(rows)+'</div></section>'

def dated(m,d,path,prev=None,nxt=None):
    ds=d["date"]; ev=d.get("events",[])
    robots="index,follow,max-image-preview:large" if ev else "noindex,follow"
    nav=[]
    if prev: nav.append(f'<a href="../{prev}/">← {esc(short(prev))}</a>')
    nav.append('<a href="../archive/">Archive</a>')
    if nxt: nav.append(f'<a href="../{nxt}/">{esc(short(nxt))} →</a>')
    body=head(f"Sports on Antenna in {m['name']} | {fmt(ds)}",f"Free over-the-air sports programming in {m['name']} for {fmt(ds)}.",f"{DOMAIN}/{m['slug']}/{ds}/",2,robots)+header(2,m)+f'''
<main class="wrap"><section class="hero"><div class="eyebrow">{esc(fmt(ds).upper())} · {esc(m["time_label"].upper())}</div>
<h1>{esc(m["name"])} sports on antenna</h1><p class="lede">Games, replays, sports talk, wrestling, racing, highlights and other sports programming available free over the air.</p></section>
{listing(d)}<nav class="archive-nav" aria-label="Date navigation">{''.join(nav)}</nav></main>'''+footer()
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(body,encoding="utf-8")

def alias(m,d,kind,ds,path):
    word="Today" if kind=="today" else "Tomorrow"
    body=head(f"Sports on Antenna {word} in {m['name']} | Free OTA Sports",f"Free over-the-air sports programming in {m['name']} {word.lower()}.",f"{DOMAIN}/{m['slug']}/sports-on-tv-{kind}/",2)+header(2,m)+f'''
<main class="wrap"><section class="hero"><div class="eyebrow">{esc(fmt(ds).upper())} · {esc(m["time_label"].upper())}</div>
<h1>{esc(m["name"])} sports on antenna {word.lower()}</h1><p class="lede">Games, replays, sports talk, wrestling, racing, highlights and other sports programming available free over the air.</p></section>
{listing(d,word+"'s listings have not been published yet.")}<nav class="archive-nav"><a href="../{ds}/">Permanent {esc(short(ds))} page</a><a href="../archive/">Browse archive</a></nav></main>'''+footer()
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(body,encoding="utf-8")

def archive(m,recs,path):
    items=[]
    for d in reversed(recs):
        n=len(d.get("events",[])); st=plural(n,"verified listing") if n else "No verified listings"
        items.append(f'<div class="archive-item"><a href="../{d["date"]}/">{esc(fmt(d["date"]))}</a><span>{esc(st)}</span></div>')
    body=head(f"{m['name']} OTA Sports Archive | Daily Antenna Sports Listings",f"Archive of free over-the-air sports listings for the {m['name']} television market.",f"{DOMAIN}/{m['slug']}/archive/",2)+header(2,m)+f'''
<main class="wrap"><section class="hero"><div class="eyebrow">{esc(m["name"].upper())} TELEVISION MARKET</div><h1>{esc(m["name"])} OTA sports archive</h1>
<p class="lede">Permanent daily over-the-air sports listings.</p></section><section class="section"><h2>Daily archive</h2><div class="archive-list">{''.join(items)}</div></section></main>'''+footer()
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(body,encoding="utf-8")

def market_page(m,now,path):
    local=now.astimezone(ZoneInfo(m["timezone"])); td=local.date().isoformat(); tm=(local.date()+timedelta(days=1)).isoformat()
    a=load_daily(m["slug"],td); b=load_daily(m["slug"],tm)
    def st(d): return "Not published" if d is None else plural(len(d.get("events",[])),"verified listing")
    body=head(f"{m['name']} OTA Sports | Free Antenna Sports Today & Tomorrow",f"Free over-the-air sports programming for the {m['name']} television market, today and tomorrow.",f"{DOMAIN}/{m['slug']}/",1)+header(1,m)+f'''
<main class="wrap"><section class="hero"><div class="eyebrow">{esc(m["name"].upper())} TELEVISION MARKET</div>
<h1>{esc(m["name"])} sports on antenna</h1><p class="lede">Verified free over-the-air sports programming for today and tomorrow.</p></section>
<section class="section"><div class="grid"><a class="card" href="sports-on-tv-today/"><h2>Today</h2><p>{esc(fmt(td))}</p><p class="count">{esc(st(a))}</p></a>
<a class="card" href="sports-on-tv-tomorrow/"><h2>Tomorrow</h2><p>{esc(fmt(tm))}</p><p class="count">{esc(st(b))}</p></a>
<a class="card" href="archive/"><h2>Archive</h2><p>Browse permanent dated listings.</p></a></div></section></main>'''+footer()
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(body,encoding="utf-8")

def home(ms,now,path):
    cards=[]
    for m in ms:
        local=now.astimezone(ZoneInfo(m["timezone"])); td=local.date().isoformat(); tm=(local.date()+timedelta(days=1)).isoformat()
        a=load_daily(m["slug"],td); b=load_daily(m["slug"],tm)
        av="not published" if a is None else plural(len(a.get("events",[])))
        bv="not published" if b is None else plural(len(b.get("events",[])))
        cards.append(f'<a class="card" href="{m["slug"]}/"><h2>{esc(m["card"])}</h2><p>Today: {esc(av)}</p><p>Tomorrow: {esc(bv)}</p></a>')
    body=head("OTA Sports | Free Over-the-Air Sports Today & Tomorrow","Free over-the-air sports programming by local television market for today and tomorrow.",DOMAIN+"/",0)+header(0)+f'''
<main class="wrap"><section class="hero"><div class="eyebrow">LOCAL ANTENNA SPORTS DIRECTORY</div>
<h1>Free sports on antenna TV today and tomorrow</h1><p class="lede">Verified local games, sports programs, replays, wrestling, racing, highlights and other sports programming across major North American television markets.</p></section>
<section class="section" id="markets"><h2>Markets</h2><div class="grid">{''.join(cards)}</div></section></main>'''+footer()
    path.write_text(body,encoding="utf-8")

def build(out,now):
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True); shutil.copytree(ROOT/"assets",out/"assets")
    ms=load_markets()
    for m in ms:
        recs=all_daily(m["slug"]); dates=[d["date"] for d in recs]
        for i,d in enumerate(recs):
            dated(m,d,out/m["slug"]/d["date"]/"index.html",dates[i-1] if i else None,dates[i+1] if i+1<len(dates) else None)
        archive(m,recs,out/m["slug"]/"archive"/"index.html")
        local=now.astimezone(ZoneInfo(m["timezone"])); td=local.date().isoformat(); tm=(local.date()+timedelta(days=1)).isoformat()
        alias(m,load_daily(m["slug"],td),"today",td,out/m["slug"]/"sports-on-tv-today"/"index.html")
        alias(m,load_daily(m["slug"],tm),"tomorrow",tm,out/m["slug"]/"sports-on-tv-tomorrow"/"index.html")
        market_page(m,now,out/m["slug"]/"index.html")
    home(ms,now,out/"index.html")
    (out/"robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://otasports.info/sitemap.xml\n",encoding="utf-8")
    (out/"CNAME").write_text("otasports.info\n",encoding="utf-8")
    (out/".nojekyll").write_text("",encoding="utf-8")
    urls=[DOMAIN+"/"]
    for m in ms:
        s=m["slug"]; urls += [f"{DOMAIN}/{s}/",f"{DOMAIN}/{s}/sports-on-tv-today/",f"{DOMAIN}/{s}/sports-on-tv-tomorrow/",f"{DOMAIN}/{s}/archive/"]
        urls += [f"{DOMAIN}/{s}/{d['date']}/" for d in all_daily(s) if d.get("events")]
    urls=list(dict.fromkeys(urls))
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"\n".join(f"  <url><loc>{esc(u)}</loc></url>" for u in urls)+"\n</urlset>\n"
    (out/"sitemap.xml").write_text(sitemap,encoding="utf-8")
    (out/"404.html").write_text(head("Page not found | OTA Sports","OTA Sports page not found.",DOMAIN+"/404.html",0,"noindex,follow")+header(0)+'''<main class="wrap"><section class="hero"><div class="eyebrow">404</div><h1>Page not found</h1><p class="lede">That listing is not here.</p></section></main>'''+footer(),encoding="utf-8")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",default="_site"); ap.add_argument("--now")
    a=ap.parse_args(); now=datetime.fromisoformat(a.now).astimezone(timezone.utc) if a.now else datetime.now(timezone.utc)
    out=Path(a.output); out=out if out.is_absolute() else ROOT/out
    build(out,now)
if __name__=="__main__": main()
