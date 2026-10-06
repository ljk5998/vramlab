#!/usr/bin/env python3
"""Compare navigation source data with a fresh Hugo production build.

Usage: python scripts/check_navigation.py public [--report result.json]
       python scripts/check_navigation.py public --baseline HEAD --report result.json

Uses the standard library. This checks static navigation contracts; it does not
claim browser, keyboard, network-error, viewport, CLS, or search-performance QA.
The optional baseline gate is for this structure-only change. CI omits it so
later, legitimate article corrections can change bodies and existing metadata.
"""
import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://vramlab.com"
KST = timezone(timedelta(hours=9))
GUIDES = {"/start-here/", "/fixes/", "/compatibility/", "/benchmarks/"}
HUBS = GUIDES
LABELS = {"/": "Home", "/start-here/": "Start here", "/fixes/": "Fixes",
          "/compatibility/": "Compatibility", "/benchmarks/": "Measurements",
          "/posts/": "All reports"}
MENU = [("Start here", "/start-here/"), ("Fixes", "/fixes/"),
        ("Compatibility", "/compatibility/"), ("Measurements", "/benchmarks/"),
        ("All reports", "/posts/"), ("Search", "/search/")]
EXISTING = {
    "wsl2-sparse-vhd-cannot-compact": "wsl2-sparse-vhd-cannot-compact",
    "move-huggingface-cache-wsl2": "move-huggingface-cache-wsl2",
    "wsl2-vhd-uncompressed-unencrypted-not-sparse": "wsl-resize-error-0xc03a001a",
    "torch-cuda-is-available-false-wsl2": "torch-cuda-is-available-false-wsl2",
    "pytorch-2-13-rtx-5060-ti-cuda-wheels": "pytorch-2-13-rtx-5060-ti-cuda-wheels",
    "llama-cpp-mixed-kv-cache-rtx-5060-ti": "llama-cpp-mixed-kv-cache-rtx-5060-ti",
    "hf-datasets-cache-wsl2": "hf-datasets-cache-wsl2",
    "m4-16gb-long-context-memory": "m4-16gb-long-context-memory",
    "hf-datasets-streaming-cache-wsl2": "hf-datasets-streaming-cache-wsl2",
}


def text(value):
    return " ".join(str(value).split())


def scalar(value):
    """Read the repository's scalar metadata; reject unsupported YAML forms.

    The checker is a schema reader, not a general YAML implementation. Unknown
    top-level fields remain opaque. Navigation accepts block lists of page/reason
    mappings or []; unsupported navigation syntax fails rather than being ignored.
    """
    value = value.strip()
    if value.startswith('"'):
        match = re.fullmatch(r'("(?:\\.|[^"\\])*")\s*(?:#.*)?', value)
        if not match:
            raise ValueError("invalid quoted scalar")
        return json.loads(match[1])
    if value.startswith("'"):
        match = re.fullmatch(r"('(?:''|[^'])*')\s*(?:#.*)?", value)
        if not match:
            raise ValueError("invalid single-quoted scalar")
        return match[1][1:-1].replace("''", "'")
    value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
    if value in {"true", "false"}:
        return value == "true"
    if value == "[]":
        return []
    return value


def frontmatter(raw):
    normalized = raw.replace(b"\r\n", b"\n")
    if normalized.startswith(b"\xef\xbb\xbf"):
        normalized = normalized[3:]
    block = re.match(rb"\A---\n(.*?)\n---(?:\n|$)(.*)\Z", normalized, re.S)
    if not block:
        raise ValueError("missing YAML frontmatter")
    lines = block[1].decode("utf-8").splitlines()
    entries, fields = {}, {}
    positions = []
    for i, line in enumerate(lines):
        key = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if key:
            if key[1] in entries:
                raise ValueError(f"duplicate frontmatter key {key[1]}")
            entries[key[1]] = key[2]
            positions.append((i, key[1]))
    for index, (start, key) in enumerate(positions):
        end = positions[index + 1][0] if index + 1 < len(positions) else len(lines)
        if key != "relatedReading":
            # Tags/images are not navigation fields; retaining their exact source
            # value also permits a strict baseline comparison without YAML deps.
            value = entries[key]
            fields[key] = scalar(value) if not value.startswith("[") else value.strip()
            continue
        if scalar(entries[key]) == []:
            if any(line.strip() and not line.lstrip().startswith("#")
                   for line in lines[start + 1:end]):
                raise ValueError("relatedReading [] also contains block items")
            fields[key] = []
            continue
        if entries[key].strip() and not entries[key].lstrip().startswith("#"):
            raise ValueError("relatedReading must be [] or a block list")
        items = []
        for line in lines[start + 1:end]:
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            entry = re.fullmatch(r"  - (page|reason):\s*(.*)", line)
            continuation = re.fullmatch(r"    (page|reason):\s*(.*)", line)
            if entry:
                items.append({entry[1]: scalar(entry[2])})
            elif continuation and items:
                if continuation[1] in items[-1]:
                    raise ValueError("duplicate relatedReading mapping key")
                items[-1][continuation[1]] = scalar(continuation[2])
            else:
                raise ValueError(f"unsupported relatedReading syntax: {line!r}")
        fields[key] = items
    return fields, block[2]


def menu_from_source():
    config = (ROOT / "hugo.yaml").read_text(encoding="utf-8")
    match = re.search(r"(?ms)^menu:\s*\n  main:\s*\n(.*?)(?=^[^ #\n]|\Z)", config)
    if not match:
        raise ValueError("menu.main block missing")
    items = []
    for line in match[1].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        first = re.fullmatch(r"    - ([\w-]+):\s*(.*)", line)
        rest = re.fullmatch(r"      ([\w-]+):\s*(.*)", line)
        if first:
            items.append({first[1]: scalar(first[2])})
        elif rest and items:
            if rest[1] in items[-1]:
                raise ValueError("duplicate menu mapping key")
            items[-1][rest[1]] = scalar(rest[2])
        else:
            raise ValueError(f"unsupported menu syntax: {line!r}")
    return sorted(items, key=lambda item: int(item["weight"]))


def as_date(value):
    result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return result.replace(tzinfo=KST) if result.tzinfo is None else result


@dataclass
class Source:
    path: Path
    ref: str
    route: str
    fields: dict
    body: bytes

    @property
    def title(self):
        return str(self.fields.get("title", ""))

    @property
    def is_report(self):
        return self.ref.startswith("/posts/")

    @property
    def published(self):
        if self.fields.get("draft", False) is not False:
            return False
        value = self.fields.get("publishDate", self.fields.get("date"))
        return value is None or as_date(value) <= datetime.now(timezone.utc)

    @property
    def publish_date(self):
        return as_date(self.fields.get("publishDate", self.fields["date"]))


class Node:
    def __init__(self, tag="", attrs=None):
        self.tag, self.attrs, self.children = tag, attrs or {}, []

    def content(self):
        return "".join(child.content() if isinstance(child, Node) else child
                       for child in self.children)

    def find(self, tag=None, cls=None, identifier=None):
        result = []
        for child in self.children:
            if isinstance(child, Node):
                if ((tag is None or child.tag == tag)
                    and (cls is None or cls in child.attrs.get("class", "").split())
                    and (identifier is None or child.attrs.get("id") == identifier)):
                    result.append(child)
                result.extend(child.find(tag, cls, identifier))
        return result


class Document(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
            "meta", "param", "source", "track", "wbr"}

    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.root, self.stack = Node(), []
        self.stack = [self.root]
        self.feed(path.read_text(encoding="utf-8"))

    def close_optional(self, tags, barriers):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag in barriers:
                return
            if self.stack[i].tag in tags:
                self.stack = self.stack[:i]
                return

    def handle_starttag(self, tag, pairs):
        if tag == "li":
            self.close_optional({"li"}, {"ol", "ul"})
        elif tag in {"td", "th"}:
            self.close_optional({"td", "th"}, {"tr"})
        elif tag == "tr":
            self.close_optional({"tr"}, {"tbody", "thead", "table"})
        if tag in {"p", "div", "section", "table", "ul", "ol", "h1", "h2", "h3"}:
            self.close_optional({"p"}, {"article", "main", "body"})
        node = Node(tag, dict(pairs))
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, pairs):
        self.handle_starttag(tag, pairs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                return

    def handle_data(self, value):
        self.stack[-1].children.append(value)


def anchors(node):
    return [(a.attrs.get("href", ""), text(a.content())) for a in node.find("a")]


def objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


class Audit:
    def __init__(self, output, baseline):
        self.output, self.baseline = output, baseline
        self.errors, self.count = [], 0
        self.details = {"baseline": {"status": "skipped", "reason": "--baseline not supplied"}}
        self.sources, self.pages = {}, {}

    def require(self, condition, message):
        self.count += 1
        if not condition:
            self.errors.append(message)
        return bool(condition)

    def page(self, route):
        key = route.lstrip("/") + "index.html"
        page = self.pages.get(key)
        self.require(page is not None, f"Missing built page {route}")
        return page.root if page else Node()

    def run(self):
        for path in sorted((ROOT / "content").rglob("*.md")):
            if path.name == "_index.md":
                continue
            fields, body = frontmatter(path.read_bytes())
            ref = "/" + path.relative_to(ROOT / "content").with_suffix("").as_posix()
            route = fields.get("url", ref.rsplit("/", 1)[0] + "/" +
                               fields.get("slug", path.stem) + "/")
            self.require(isinstance(route, str) and route.startswith("/")
                         and route.endswith("/"), f"Invalid route for {ref}: {route}")
            self.sources[ref] = Source(path, ref, route, fields, body)
        published = [source for source in self.sources.values() if source.published]
        reports = [source for source in published if source.is_report]
        routes = {source.route: source for source in published}
        self.require(len(routes) == len(published), "Duplicate published content URL")
        report_routes = {source.route for source in reports}
        self.details.update(source_reports=len(reports), searchable_expected=len(reports) + 4)
        for filename, slug in EXISTING.items():
            source = self.sources.get("/posts/" + filename)
            self.require(source is not None and source.published and
                         source.route == f"/posts/{slug}/", f"Existing URL changed: {slug}")
        for path in sorted(self.output.rglob("*.html")):
            self.pages[path.relative_to(self.output).as_posix()] = Document(path)
        self.details["built_html_pages"] = len(self.pages)
        self.require(bool(self.pages), "No built HTML found")

        menu_items = menu_from_source()
        configured = [(item.get("name"), item.get("url")) for item in menu_items]
        self.require(configured == MENU, f"menu.main differs from approved six entries: {configured}")
        self.require(len({item.get("identifier") for item in menu_items}) == 6,
                     "Menu identifiers missing or duplicated")
        source_base = (ROOT / "themes/LabDraft/layouts/baseof.html").read_text(encoding="utf-8")
        self.require("range site.Menus.main" in source_base, "Main menu is not config-driven")
        for key, document in self.pages.items():
            root = document.root
            navs = root.find("nav", cls="main-nav")
            if not key.startswith("lab/diagrams/"):
                self.require(len(navs) == 1, f"Missing or duplicated main nav: {key}")
            for nav in navs:
                self.require([(label, href) for href, label in anchors(nav)] == configured,
                             f"Built menu differs from source: {key}")

        for source in reports:
            page = self.page(source.route)
            canonicals = [n.attrs.get("href") for n in page.find("link")
                          if n.attrs.get("rel") == "canonical"]
            self.require(canonicals == [ORIGIN + source.route], f"Canonical changed: {source.ref}")
            headings = page.find("h1")
            self.require(len(headings) == 1 and text(headings[0].content()) == text(source.title),
                         f"Report title mismatch: {source.ref}")
            hub_ref = source.fields.get("primaryHub")
            hub = self.sources.get(hub_ref) if isinstance(hub_ref, str) else None
            valid_hub = hub is not None and hub.published and hub.route in HUBS
            self.require(valid_hub, f"Invalid primaryHub: {source.ref} -> {hub_ref}")
            related = source.fields.get("relatedReading")
            valid_related = isinstance(related, list) and len(related) <= 2
            self.require(valid_related, f"relatedReading must be a list of 0..2: {source.ref}")
            expected, seen = [], {source.route}
            if valid_hub:
                seen.add(hub.route)
                returns = page.find(cls="topic-return")
                self.require(len(returns) == 2, f"Need top and bottom topic returns: {source.ref}")
                for node in returns:
                    self.require([href for href, _ in anchors(node)] == [hub.route],
                                 f"Wrong topic return RelPermalink: {source.ref}")
            for item in related if isinstance(related, list) else []:
                mapping_ok = isinstance(item, dict) and set(item) == {"page", "reason"}
                self.require(mapping_ok, f"Malformed relatedReading mapping: {source.ref}")
                if not mapping_ok:
                    continue
                ref, reason = item["page"], item["reason"]
                target = self.sources.get(ref) if isinstance(ref, str) else None
                allowed = target is not None and target.published and (target.is_report or target.route in GUIDES)
                self.require(allowed, f"Related target missing, unpublished or disallowed: {source.ref} -> {ref}")
                self.require(isinstance(reason, str) and bool(reason.strip()), f"Empty/non-string reason: {source.ref}")
                if allowed:
                    self.require(target.route not in seen, f"Related self/duplicate/primary hub: {source.ref} -> {ref}")
                    seen.add(target.route)
                    expected.append((target.route, text(target.title), text(reason)))
            sections = page.find("section", cls="next-reading")
            self.require(len(sections) == (1 if expected else 0), f"Related section missing or unexpected: {source.ref}")
            actual = []
            for section in sections:
                for item in section.find("li"):
                    links, reasons = anchors(item), item.find(cls="reading-reason")
                    self.require(len(links) == 1 and len(reasons) == 1, f"Related row incomplete: {source.ref}")
                    if len(links) == 1 and len(reasons) == 1:
                        actual.append((links[0][0], links[0][1], text(reasons[0].content())))
            self.require(actual == expected, f"Built next reading differs from source: {source.ref}")

        hub_links = {}
        for route in HUBS:
            bodies = self.page(route).find(cls="post-content")
            self.require(len(bodies) == 1, f"Hub content missing: {route}")
            hub_links[route] = {href for body in bodies for href, _ in anchors(body)}
        for route in report_routes:
            self.require(any(route in links for links in hub_links.values()), f"Report absent from hub bodies: {route}")
        fixes = self.page("/fixes/")
        self.require(bool(fixes.find(identifier="disk-space-and-model-caches")), "Existing Fixes fragment was removed")

        home = self.page("/")
        actions = home.find(cls="hero-actions")
        first_links = anchors(actions[0]) if actions else []
        self.require(bool(first_links) and first_links[0][0] == "/start-here/", "Home primary action does not open Start here")
        topics = home.find("nav", cls="hero-topics")
        cards = topics[0].find("a", cls="topic-card") if len(topics) == 1 else []
        self.require([card.attrs.get("href") for card in cards] == ["/fixes/", "/compatibility/", "/benchmarks/"], "Home task cards missing or wrong")
        introduction, scenes = home.find(cls="hero-introduction"), home.find(cls="scene-panel")
        self.require(len(introduction) == 1 and len(introduction[0].find("nav", cls="hero-topics")) == 1, "Task choices are not in hero introduction")
        hero = home.find("section", cls="hero")
        children = [child for child in hero[0].children if isinstance(child, Node)] if hero else []
        self.require(bool(introduction) and bool(scenes) and introduction[0] in children and scenes[0] in children and children.index(introduction[0]) < children.index(scenes[0]), "Hero task choices do not precede scene in DOM")
        latest = home.find("section", identifier="latest-reports")
        rows = latest[0].find("article", cls="report-row") if len(latest) == 1 else []
        expected_count = min(2, len(reports))
        self.require(len(rows) == expected_count, "Latest reports must contain the latest two published reports")
        displayed = []
        for row in rows:
            links = anchors(row)
            source = routes.get(links[0][0]) if len(links) == 1 else None
            valid = source is not None and source.is_report and source.published
            self.require(valid, "Latest report must link one published report")
            if not valid:
                continue
            displayed.append(source)
            self.require(links == [(source.route, text(source.title))], "Latest report title/URL differs from source")
            times = row.find("time")
            expected_date = as_date(source.fields["date"]).strftime("%Y-%m-%d")
            self.require(len(times) == 1 and times[0].attrs.get("datetime") == expected_date, f"Latest report date differs from source: {source.ref}")
        displayed_routes = {source.route for source in displayed}
        displayed_dates = [source.publish_date for source in displayed]
        self.require(len(displayed_routes) == len(displayed), "Latest reports contain duplicate reports")
        self.require(displayed_dates == sorted(displayed_dates, reverse=True), "Latest reports are not in descending publish-date order")
        if expected_count:
            # Hugo may order equal dates differently from source-path order.
            # Any report at the second-item cutoff is valid, but a newer one may
            # never be omitted and an older one may never occupy the two slots.
            cutoff = sorted((source.publish_date for source in reports), reverse=True)[expected_count - 1]
            self.require(all(source.publish_date >= cutoff for source in displayed), "Latest reports include a report older than the publish-date cutoff")
            newer_routes = {source.route for source in reports if source.publish_date > cutoff}
            self.require(newer_routes <= displayed_routes, "Latest reports omit a report newer than the publish-date cutoff")
        unpublished = {source.route for source in self.sources.values() if not source.published}
        self.require(not ({href for href, _ in anchors(home)} & unpublished), "Home exposes draft or future content")
        archives = home.find("section", cls="archive-section")
        archive_urls = {href for archive in archives for row in archive.find("article", cls="report-row") for href, _ in anchors(row)}
        self.require(archive_urls == report_routes, "Home archive does not expose all and only published reports")

        index = json.loads((self.output / "index.json").read_text(encoding="utf-8"))
        indexed = [urlsplit(item["permalink"]).path for item in index]
        self.require(len(indexed) == len(set(indexed)), "Search index has duplicate URLs")
        self.require(set(indexed) == report_routes | GUIDES, "Search index must be N published reports plus four guides")
        for item in index:
            route = urlsplit(item["permalink"]).path
            self.require(item["permalink"] == ORIGIN + route, f"Search index non-production permalink: {route}")
            self.require(route in routes and text(item.get("title", "")) == text(routes[route].title), f"Search title differs from source: {route}")
        for ref in ["/about", "/contact", "/privacy-policy", "/search-collector"]:
            self.require(ref in self.sources and self.sources[ref].fields.get("searchHidden") is True, f"Information page not searchHidden: {ref}")

        breadcrumb_count = 0
        for key, document in self.pages.items():
            page = document.root
            schemas = []
            for script in page.find("script"):
                if script.attrs.get("type") == "application/ld+json":
                    schemas.extend(objects(json.loads(script.content())))
            route = "/" + key.removesuffix("index.html")
            postings = [obj for obj in schemas if obj.get("@type") == "BlogPosting"]
            self.require(len(postings) == (1 if route in report_routes else 0), f"BlogPosting scope incorrect: {key}")
            breadcrumbs = page.find("nav", cls="breadcrumbs")
            lists = [obj for obj in schemas if obj.get("@type") == "BreadcrumbList"]
            if breadcrumbs:
                breadcrumb_count += 1
                self.require(len(breadcrumbs) == 1 and len(lists) == 1, f"Breadcrumb/JSON-LD duplicated or missing: {key}")
                ordered = breadcrumbs[0].find("ol")
                self.require(len(ordered) == 1, f"Breadcrumb must be an ordered list: {key}")
                visible = []
                for item in ordered[0].find("li") if len(ordered) == 1 else []:
                    links = anchors(item)
                    current = [node for node in item.find("span") if node.attrs.get("aria-current") == "page"]
                    self.require((len(links), len(current)) in {(1, 0), (0, 1)}, f"Malformed breadcrumb item: {key}")
                    if links:
                        visible.append((links[0][0], links[0][1]))
                    elif current:
                        visible.append((route, text(current[0].content())))
                structured = []
                for position, item in enumerate(lists[0].get("itemListElement", []) if lists else [], 1):
                    self.require(item.get("position") == position and item.get("@type") == "ListItem", f"Breadcrumb position/type incorrect: {key}")
                    url = item.get("item", "")
                    self.require(url.startswith(ORIGIN + "/"), f"Breadcrumb URL is not production: {key}")
                    structured.append((urlsplit(url).path, text(item.get("name", ""))))
                self.require(visible == structured, f"Visible breadcrumb disagrees with JSON-LD: {key}")
                if route in report_routes:
                    source = routes[route]
                    hub = self.sources.get(source.fields.get("primaryHub"))
                    if hub:
                        self.require(visible == [("/", "Home"), (hub.route, LABELS[hub.route]), (route, text(source.title))], f"Breadcrumb differs from report primary hub: {key}")
            if route in report_routes | GUIDES:
                self.require(bool(breadcrumbs), f"Missing visible breadcrumb: {route}")
        self.details["breadcrumb_pages"] = breadcrumb_count

        streaming = self.page("/posts/hf-datasets-streaming-cache-wsl2/")
        images = [node for node in streaming.find("img") if urlsplit(node.attrs.get("src", "")).path == "/images/hf-streaming-cache-and-responses.svg"]
        self.require(len(images) == 1 and images[0].attrs.get("width") == "500" and images[0].attrs.get("height") == "860", "Streaming SVG does not reserve its 500x860 intrinsic ratio")

        # Static counterparts of the six reader journeys. Runtime navigation and
        # viewport QA remain separate and must not be inferred from these links.
        journey_links = {
            "/start-here/": {"/fixes/#disk-space-and-model-caches", "/posts/move-huggingface-cache-wsl2/"},
            "/fixes/": {"/posts/wsl2-sparse-vhd-cannot-compact/", "/posts/move-huggingface-cache-wsl2/", "/posts/hf-datasets-cache-wsl2/", "/posts/wsl-resize-error-0xc03a001a/"},
            "/compatibility/": {"/posts/torch-cuda-is-available-false-wsl2/", "/posts/pytorch-2-13-rtx-5060-ti-cuda-wheels/"},
            "/benchmarks/": {"/posts/m4-16gb-long-context-memory/"},
        }
        for route, required in journey_links.items():
            urls = {href for body in self.page(route).find(cls="post-content") for href, _ in anchors(body)}
            self.require(required <= urls, f"Reader journey missing from guide body: {route}: {sorted(required - urls)}")
        if self.baseline:
            baseline_rows = []
            for filename in EXISTING:
                source = self.sources.get("/posts/" + filename)
                if source is None:
                    continue
                relative = source.path.relative_to(ROOT).as_posix()
                result = subprocess.run(["git", "-C", str(ROOT), "show", f"{self.baseline}:{relative}"], capture_output=True, check=False)
                if not self.require(result.returncode == 0, f"Cannot read baseline {self.baseline}:{relative}"):
                    continue
                previous, previous_body = frontmatter(result.stdout)
                same_body = source.body == previous_body
                self.require(same_body, f"Existing report body changed: {relative}")
                self.require(all(source.fields.get(key) == value for key, value in previous.items()), f"Existing report metadata changed: {relative}")
                baseline_rows.append({"file": relative, "body_unchanged": same_body,
                                      "body_sha256": hashlib.sha256(source.body).hexdigest()})
            self.details["baseline"] = {"status": "checked", "ref": self.baseline,
                                        "line_endings": "Git-normalized LF; remaining body bytes exact",
                                        "reports": baseline_rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build", nargs="?", default="public", type=Path)
    parser.add_argument("--report", "--json", dest="report", type=Path)
    parser.add_argument("--baseline", help="Git ref for this structure-only body/metadata preservation gate")
    args = parser.parse_args()
    audit = Audit(args.build.resolve(), args.baseline)
    try:
        audit.run()
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        audit.errors.append(f"Audit could not complete: {type(error).__name__}: {error}")
    result = {"status": "FAIL" if audit.errors else "PASS", "build": str(audit.output),
              "checks": audit.count, "errors": audit.errors, "details": audit.details,
              "scope": "Static source/build comparison; runtime/browser checks are separate."}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for error in audit.errors:
        print(f"FAIL: {error}")
    print(f"{result['status']}: {audit.count} navigation checks; {audit.details.get('source_reports', 0)} published reports.")
    return 1 if audit.errors else 0


if __name__ == "__main__":
    sys.exit(main())
