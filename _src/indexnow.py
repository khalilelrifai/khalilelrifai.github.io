"""Notify IndexNow of deployed public page changes; no third-party dependencies."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

HOST = "abrprotowing.com"
BASE = "https://" + HOST
KEY = "82198492edc9c3570c179da012ce3713"
KEY_PATH = KEY + ".txt"
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}

def git(*args):
    return subprocess.check_output(["git", *args], text=True)

def pages(xml):
    urls = [el.text for el in ET.fromstring(xml).findall("s:url/s:loc", NS)]
    result = {}
    for url in urls:
        p = urlsplit(url)
        if p.scheme != "https" or p.netloc != HOST or p.query or p.fragment or not p.path.startswith("/"):
            raise ValueError("Unexpected sitemap URL: " + url)
        path = p.path.lstrip("/")
        if not path or path.endswith("/"):
            path += "index.html"
        if not path.endswith(".html") or ".." in Path(path).parts:
            raise ValueError("Unexpected sitemap page: " + path)
        result[path] = url
    return result

def get(url):
    req = Request(url, headers={"User-Agent": "ABR-Pro-Towing-IndexNow/1.0", "Cache-Control": "no-cache"})
    with urlopen(req, timeout=20) as response:
        return response.read()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--before", default="")
    args = parser.parse_args()
    current = pages(Path("sitemap.xml").read_text())
    if args.all or not args.before or set(args.before) == {"0"}:
        selected = dict(current)
    else:
        previous = pages(git("show", args.before + ":sitemap.xml"))
        changed = set(git("diff", "--name-only", args.before, "HEAD").splitlines())
        selected = {p:u for p,u in current.items() if p in changed or p not in previous or KEY_PATH in changed}
        selected.update({p:u for p,u in previous.items() if p not in current})
        # Changes to shared assets affect all pages.
        if any(p.startswith(("css/", "js/", "img/")) for p in changed):
            selected.update(current)
    urls = sorted(set(selected.values()))
    print("IndexNow URL selection:", json.dumps(urls))
    if args.dry_run or not urls:
        return
    if Path(KEY_PATH).read_text().strip() != KEY:
        raise RuntimeError("Local IndexNow key mismatch")
    # Wait for Pages to publish this version, rather than notifying on an old deployment.
    expected = {u: Path(p).read_bytes() for p,u in selected.items() if p in current}
    for attempt in range(20):
        try:
            if get(BASE + "/" + KEY_PATH).decode().strip() != KEY:
                raise RuntimeError("Public key does not match")
            if any(get(u) != content for u,content in expected.items()):
                raise RuntimeError("A changed page has not reached the public website")
            break
        except Exception as error:
            print("Waiting for deployment:", str(error), flush=True)
            if attempt == 19:
                raise
            time.sleep(20)
    payload = {"host": HOST, "key": KEY, "keyLocation": BASE + "/" + KEY_PATH, "urlList": urls}
    req = Request("https://api.indexnow.org/indexnow", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    with urlopen(req, timeout=30) as response:
        if response.status not in (200, 202):
            raise RuntimeError("Unexpected IndexNow response " + str(response.status))
        print("IndexNow HTTP", response.status, "for", len(urls), "URLs; indexing is not guaranteed.")

if __name__ == "__main__":
    main()
