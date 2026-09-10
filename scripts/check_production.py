#!/usr/bin/env python3
"""Check the deployable HTML/SEO boundary using only the Python standard library.

Usage: python scripts/check_production.py [public]
Works with minified and unminified Hugo output. Does not fetch external URLs.
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET

OUTPUT = Path(sys.argv[1] if len(sys.argv) > 1 else "public").resolve()
ORIGIN = "https://vramlab.com"
ERRORS = []


def require(condition, message):
    if not condition:
        ERRORS.append(message)


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.metadata = {}
        self.canonical = []
        self.refs = []
        self.ids = set()
        self.content = path.read_text(encoding="utf-8")
        self.feed(self.content)

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if tag == "meta":
            self.metadata[attrs.get("name", attrs.get("property", ""))] = attrs.get("content", "")
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical.append(attrs.get("href"))
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag in {"a", "link", "script", "img", "iframe", "source", "audio", "video"}:
            for key in ("href", "src"):
                if attrs.get(key):
                    self.refs.append(attrs[key])


pages = {p.relative_to(OUTPUT).as_posix(): Page(p) for p in OUTPUT.rglob("*.html")}
require("index.html" in pages, "Missing homepage")
if not pages:
    raise SystemExit("FAIL: no built HTML found")
home = pages["index.html"]
index = json.loads((OUTPUT / "index.json").read_text(encoding="utf-8"))
reports = sorted({urlsplit(item["permalink"]).path for item in index
                  if urlsplit(item["permalink"]).path.startswith("/posts/")
                  and urlsplit(item["permalink"]).path != "/posts/"})
require(len(reports) >= 7, "Expected the seven existing reports to remain available")
require("Small hardware." in home.content and "Deep experiments." in home.content,
        "Approved homepage design is missing")
require("/lab/scene.js" in home.refs, "Homepage 3D entrypoint is missing")
require("cloudflareinsights" in home.content, "Existing production analytics is missing")

indexable = ["/"] + reports + ["/start-here/", "/fixes/", "/compatibility/", "/benchmarks/", "/about/"]
for route in indexable:
    key = route.lstrip("/") + "index.html"
    page = pages.get(key)
    require(page is not None, f"Missing page: {route}")
    if page is None:
        continue
    require(page.metadata.get("robots") == "index, follow", f"Unexpected robots: {route}")
    require(page.canonical == [ORIGIN + route], f"Unexpected canonical: {route}")
    has_post_schema = bool(re.search(r'"@type"\s*:\s*"BlogPosting"', page.content))
    require(has_post_schema == (route in reports), f"Incorrect BlogPosting scope: {route}")

for route in ["/search/", "/tags/", "/categories/"]:
    page = pages.get(route.lstrip("/") + "index.html")
    require(page is not None and page.metadata.get("robots") == "noindex, follow",
            f"Reader-only page indexing policy changed: {route}")

sitemap = ET.parse(OUTPUT / "sitemap.xml")
locations = {node.text for node in sitemap.iter() if node.tag.endswith("}loc")}
for route in reports:
    require(ORIGIN + route in locations, f"Report missing from sitemap: {route}")
require(all(url and url.startswith(ORIGIN + "/") and not
            any(part in url for part in ("/search/", "/tags/", "/categories/"))
            for url in locations), "Sitemap includes excluded or non-production URLs")
feed = ET.parse(OUTPUT / "index.xml")
feed_items = feed.findall("./channel/item")
require(len(feed_items) == len(reports), "RSS report count differs from search index")
require(all(urlsplit(item.findtext("link", "")).path in reports for item in feed_items),
        "RSS contains a non-report item")
robots = (OUTPUT / "robots.txt").read_text(encoding="utf-8")
require(not re.search(r"(?m)^Disallow:\s*/", robots), "Production robots blocks crawling")
require(f"Sitemap: {ORIGIN}/sitemap.xml" in robots, "Production robots sitemap is missing")

references = 0
for relative_path, page in pages.items():
    # The standalone, frozen Archify viewer is not a Hugo content page, but its
    # concrete resource references are still checked below.
    if not relative_path.startswith("lab/diagrams/"):
        require(not any(marker in page.content for marker in
                        ("DESIGN STUDY 01", "Design draft", "Local preview", "127.0.0.1:1313", "localhost:1313")),
                f"Review-only content leaked: {relative_path}")
    page_url = urljoin(ORIGIN + "/", relative_path.removesuffix("index.html"))
    for reference in page.refs:
        parsed = urlsplit(urljoin(page_url, reference))
        if parsed.scheme not in {"http", "https"} or parsed.netloc != "vramlab.com":
            continue
        target = OUTPUT / unquote(parsed.path.lstrip("/"))
        require(target.exists() or (target / "index.html").exists(),
                f"Broken local reference: {relative_path} -> {reference}")
        references += 1

diagram = OUTPUT / "lab/diagrams/dataset-cache.html"
require(diagram.exists(), "Archify diagram is missing")
if diagram.exists():
    require(hashlib.sha256(diagram.read_bytes()).hexdigest() ==
            "1cb401089c336ce53ef94dc2a2f2dfc670d5989c2f3a107187f7d997594d396d",
            "Frozen Archify artifact changed")
module = OUTPUT / "lab/vendor/three.module.min.js"
require(module.exists(), "Three.js module is missing")
if module.exists():
    for relative_import in re.findall(r'from\s*[\"\'](\.[^\"\']+)[\"\']', module.read_text(encoding="utf-8")):
        require((module.parent / relative_import).is_file(), f"Missing Three.js dependency: {relative_import}")

if ERRORS:
    print("\n".join(f"FAIL: {error}" for error in ERRORS))
    raise SystemExit(1)
print(f"PASS: {len(reports)} reports, {len(locations)} sitemap URLs, "
      f"{len(pages)} HTML files, {references} local references; production SEO and review isolation verified.")
