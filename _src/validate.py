"""Check generated site without third-party dependencies."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, re, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
S = json.loads((ROOT / "_src/site.json").read_text())
DOMAIN = S["domain"]
PROHIBITED = re.compile(r"\b(?:highways?|QEW|Gardiner|shoulders?|401|403|410|407|427)\b", re.I)
class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[]; self.canonical=[]; self.ids=[]; self.h1=0; self.title=""; self.in_title=False
        self.meta={}; self.schema=[]; self.in_schema=False; self.raw=""; self.text=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=="h1": self.h1+=1
        if tag=="title": self.in_title=True
        if a.get("id"): self.ids.append(a["id"])
        if tag=="link" and a.get("rel")=="canonical": self.canonical.append(a.get("href"))
        if tag=="meta" and a.get("name"): self.meta[a["name"]]=a.get("content","")
        for k in ("href","src"):
            if a.get(k,"").startswith("/") and not a[k].startswith("//"): self.links.append(a[k])
        if tag=="script" and a.get("type")=="application/ld+json": self.in_schema=True; self.raw=""
    def handle_endtag(self,tag):
        if tag=="title": self.in_title=False
        if tag=="script" and self.in_schema: self.schema.append(json.loads(self.raw)); self.in_schema=False
    def handle_data(self,d):
        if self.in_title: self.title+=d
        if self.in_schema: self.raw+=d
        else: self.text.append(d)
def parse(p):
    page=Page(); page.feed(p.read_text()); return page
def target(path):
    p=ROOT / unquote(path.lstrip("/"))
    return p / "index.html" if p.is_dir() else p
pages=[p for p in ROOT.glob("*.html")]+list((ROOT/"services").glob("*.html"))
parsed={p:parse(p) for p in pages}
sitemap=ET.parse(ROOT/"sitemap.xml")
urls=[e.text for e in sitemap.findall(".//{*}loc")]
assert len(urls)==len(set(urls)) and len(urls)>=10
titles=set(); descriptions=set()
for url in urls:
    assert url.startswith(DOMAIN+"/"),url
    p=target(urlsplit(url).path); page=parsed[p]
    assert page.canonical==[url],(p,page.canonical)
    assert "noindex" not in page.meta.get("robots",""),p
    assert page.h1==1,(p,page.h1)
    assert page.title not in titles and page.title,p
    titles.add(page.title)
    desc=page.meta.get("description","")
    assert desc and desc not in descriptions,p
    descriptions.add(desc)
    assert page.schema,p
    entities=[e for graph in page.schema for e in graph.get("@graph",[]) if e.get("@id")==DOMAIN+"/#business"]
    assert len(entities)==1,p
    entity=entities[0]
    assert entity["name"]==S["name"] and "geo" not in entity and "aggregateRating" not in entity and "priceRange" not in entity,p
    assert entity["telephone"]==S["phone_schema"],p
    assert entity["address"]["addressLocality"]=="Mississauga",p
    assert "Restricted towing zones are excluded." in p.read_text(),p
for p,page in parsed.items():
    assert len(page.ids)==len(set(page.ids)),(p,"duplicate id")
    for raw in page.links:
        u=urlsplit(raw); t=target(u.path)
        assert t.exists(),(p,raw)
        if u.fragment and t in parsed: assert unquote(u.fragment) in parsed[t].ids,(p,raw)
    # Check customer-visible copy, descriptions, and structured data; not numerical SVG geometry.
    for content in [" ".join(page.text), page.meta.get("description",""), json.dumps(page.schema,ensure_ascii=False)]:
        # JSON-LD has no highway references; phone numbers or street numbers are not matched here.
        assert not PROHIBITED.search(content),(p,PROHIBITED.search(content).group() if PROHIBITED.search(content) else "")
assert "abrprotowing.com"==(ROOT/"CNAME").read_text().strip()
robots=(ROOT/"robots.txt").read_text()
for bot in ["Googlebot","Bingbot","OAI-SearchBot"]: assert f"User-agent: {bot}\nAllow: /" in robots,bot
assert "User-agent: GPTBot\nDisallow: /" in robots
assert not PROHIBITED.search((ROOT/"llms.txt").read_text())
assert (ROOT/"img/abr-pro-logo.webp").read_bytes()[:4]==b"RIFF"
for p in [ROOT/"index.html",ROOT/"reviews.html"]:
    assert S["gbp_owner_share_url"] in p.read_text(),p
assert not S.get("google_reviews",{}).get("enabled") or all(S["google_reviews"].get(k) for k in ["place_id","browser_key"])
if S.get("google_reviews",{}).get("enabled"):
    for p in [ROOT/"index.html", ROOT/"reviews.html"]:
        content = p.read_text()
        assert 'class="live-reviews"' in content, p
        assert S["google_reviews"]["place_id"] in content, p
        assert S["gbp_review_url"] in content, p
print(f"PASS: {len(pages)} HTML pages; {len(urls)} sitemap URLs; schema, local links, identity, crawler access, review fallback and restricted-zone regression checks")
