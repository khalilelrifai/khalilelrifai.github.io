"""Build a minimal Cloudflare Pages release without browser credentials."""
from pathlib import Path
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
KEY_PATTERN = re.compile(rb"AIza[0-9A-Za-z_-]{35}")

def main():
    subprocess.run([sys.executable, str(ROOT / "_src/build.py")], check=True)
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    paths = set()
    for node in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc"):
        url = node.text
        if not url.startswith("https://abrprotowing.com/"):
            raise ValueError("Unexpected sitemap URL")
        path = url.removeprefix("https://abrprotowing.com/")
        paths.add(path + "index.html" if not path or path.endswith("/") else path)
    paths.update({"404.html", "thank-you.html", "service.html", "booking.html", "team.html", "testimonial.html"})
    paths.update(p.name for p in ROOT.glob("google*.html") if re.fullmatch(r"google[0-9a-zA-Z]+\.html", p.name))
    if not any(p.startswith("google") for p in paths):
        raise RuntimeError("Google verification file missing")
    aliases = {}
    for path in sorted(paths):
        src = ROOT / path
        html = src.read_text(encoding="utf-8")
        html = re.sub(r' data-key="[^"]+"', '', html)
        # Preserve the original public .html URL, bypass Pages HTML redirects.
        if path == "index.html" or path.endswith("/index.html") or path == "404.html":
            dest = DIST / path
        else:
            dest = DIST / ("site-html-assets/" + path + ".page")
            aliases["/" + path] = "/" + dest.relative_to(DIST).as_posix()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")
    for name in ["css", "js", "img"]:
        shutil.copytree(ROOT / name, DIST / name)
    for name in ["favicon.svg", "robots.txt", "sitemap.xml", "llms.txt", "BingSiteAuth.xml"]:
        shutil.copy2(ROOT / name, DIST / name)
    keys = [p for p in ROOT.glob("*.txt") if re.fullmatch(r"[a-f0-9]{32}\.txt", p.name)]
    if not keys:
        raise RuntimeError("IndexNow verification key missing")
    for p in keys:
        shutil.copy2(p, DIST / p.name)
    js = (DIST / "js/google-reviews.js").read_text(encoding="utf-8")
    start = js.index("  function loadLibrary(")
    end = js.index("  function stars(", start)
    js = js[:start] + '''  function getPlace() {
    if (!request) request = (async () => {
      const response = await fetch("/api/reviews", {
        method: "POST", headers: {"X-ABR-Reviews": "1"},
        credentials: "same-origin", cache: "no-store"
      });
      if (!response.ok) throw new Error("Reviews unavailable");
      return response.json();
    })().catch(error => { request = undefined; throw error; });
    return request;
  }
''' + js[end:]
    js = js.replace("let library, request;", "let request;")
    (DIST / "js/google-reviews.js").write_text(js, encoding="utf-8")
    worker = (ROOT / "_src/cloudflare_worker.mjs").read_text(encoding="utf-8")
    if worker.count("/*__HTML_ALIASES__*/{}") != 1:
        raise RuntimeError("Worker alias placeholder missing")
    worker = worker.replace("/*__HTML_ALIASES__*/{}", json.dumps(aliases, sort_keys=True))
    (DIST / "_worker.js").write_text(worker, encoding="utf-8")
    (DIST / "_routes.json").write_text(json.dumps({"version":1,"include":["/*"],"exclude":["/css/*","/js/*","/img/*","/favicon.svg"]}),encoding="utf-8")
    (DIST / "_headers").write_text("""/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: DENY
  Permissions-Policy: camera=(), microphone=(), geolocation=()
/js/*
  Cache-Control: public, max-age=300
/css/*
  Cache-Control: public, max-age=300
""",encoding="utf-8")
    for file in DIST.rglob("*"):
        if file.is_file() and KEY_PATTERN.search(file.read_bytes()):
            raise RuntimeError("Credential detected in output: " + str(file.relative_to(DIST)))
    if "maps.googleapis.com/maps/api/js" in js or "data-key=" in (DIST / "index.html").read_text():
        raise RuntimeError("Legacy browser authentication still present")
    print("Cloudflare output validated: static pages, exact public URL aliases, verification files, no Google API key.")

if __name__ == "__main__":
    main()
