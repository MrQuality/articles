"""Check generated pages, internal destinations, and the established article URL."""
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET

from build import ROOT, build


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.ids, self.links, self.canonicals = set(), [], []
        self.h1_count = 0
        self.feed(source)

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                raise ValueError(f'Duplicate ID: {attrs["id"]}')
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if attrs.get(key):
                self.links.append(attrs[key])
        if tag == "h1":
            self.h1_count += 1
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs["href"])


def check():
    generated = build()
    for name, expected in generated.items():
        actual = (ROOT / name).read_text(encoding="utf-8")
        if actual != expected:
            raise ValueError(f"Stale generated file: {name}; run python build.py")
    paths = list(ROOT.glob("*.html")) + list((ROOT / "generation-vii").rglob("*.html"))
    pages = {path.resolve(): Page(path.read_text(encoding="utf-8")) for path in paths}
    for path, page in pages.items():
        if page.h1_count != 1:
            raise ValueError(f"Expected one H1: {path.relative_to(ROOT)}")
        for raw in page.links:
            url = urlsplit(raw)
            if url.scheme or url.netloc:
                continue
            target = (ROOT / unquote(url.path).removeprefix("/articles/")) if url.path.startswith("/articles/") else (path.parent / unquote(url.path)) if url.path else path
            target = target.resolve()
            if target.is_dir():
                target /= "index.html"
            if not target.is_relative_to(ROOT) or not target.is_file():
                raise ValueError(f"Broken internal link in {path.relative_to(ROOT)}: {raw}")
            if url.fragment and (target not in pages or unquote(url.fragment) not in pages[target].ids):
                raise ValueError(f"Broken anchor in {path.relative_to(ROOT)}: {raw}")
    article_path = (ROOT / "generation-vii/index.html").resolve()
    canonical = "https://mrquality.github.io/articles/generation-vii/"
    if pages[article_path].canonicals != [canonical] or "experiments" not in pages[article_path].ids:
        raise ValueError("The shared Generation VII URL and #experiments anchor must be preserved")
    article = article_path.read_text(encoding="utf-8")
    if article.count('data-section-visual="') != 6 or article.count('<iframe class="') != 2:
        raise ValueError("Generation VII must retain its six later-section visuals and two experiment animations")
    feed = ET.parse(ROOT / "feed.xml")
    config = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
    links = [item.findtext("link") for item in feed.findall("./channel/item")]
    if set(links) != {f'{config["url"]}/{item["slug"]}/' for item in config["publications"]}:
        raise ValueError("RSS must contain every publication at its canonical URL")
    ET.parse(ROOT / "sitemap.xml")
    print(f"Checked {len(pages)} HTML pages: internal files and anchors, canonical article URL, visuals, RSS, sitemap, and generated-source consistency.")


if __name__ == "__main__":
    check()
