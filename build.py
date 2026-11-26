"""Build the publication site without changing its established GitHub Pages URLs.

Edit article Markdown, site.json, templates, or shared assets, then run this file.
Generated HTML is committed so Pages can continue serving main's root directory.
"""
import argparse
from datetime import date, datetime, timezone
from email.utils import format_datetime
from html import escape
from html.parser import HTMLParser
import json
import math
import posixpath
from pathlib import Path
import re
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def plain(html):
    parser = Text()
    parser.feed(html)
    return " ".join(parser.parts)


def template(name, **values):
    source = (ROOT / "templates" / f"{name}.html").read_text(encoding="utf-8")
    result = re.sub(r"\{\{(\w+)\}\}", lambda match: str(values[match[1]]), source)
    return "\n".join(line.rstrip() for line in result.splitlines()) + "\n"


def render_markdown(source):
    md = MarkdownIt("commonmark", {"html": True}).enable("table")
    tokens = md.parse(source)
    # The first heading, subtitle and byline are displayed by the shared header.
    if len(tokens) < 9 or tokens[0].tag != "h1" or tokens[3].type != "paragraph_open" or tokens[6].type != "paragraph_open":
        raise ValueError("Publication source must begin with an H1 title, subtitle paragraph, and byline paragraph")
    deck = plain(md.renderInline(tokens[4].content))
    tokens = tokens[9:]
    toc, used = [], set()
    for index, token in enumerate(tokens):
        if token.type != "heading_open":
            continue
        title = plain(md.renderInline(tokens[index + 1].content))
        anchor = "experiments" if title.startswith("4. Two small experiments") else re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        if anchor in used:
            raise ValueError(f"Duplicate heading: {title}")
        used.add(anchor)
        token.attrSet("id", anchor)
        if token.tag == "h2":
            toc.append((anchor, title))
    html = md.renderer.render(tokens, md.options, {})
    # Tables remain accessible at narrow widths, including the original visuals.
    html = re.sub(r"(<table\b.*?</table>)", r'<div class="table-scroll" tabindex="0" role="region" aria-label="Scrollable data table">\1</div>', html, flags=re.S)
    minutes = math.ceil(len(re.findall(r"\b[\w'-]+\b", plain(html))) / 220)
    return html, deck, toc, minutes


def build():
    config = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
    base = config["url"].rstrip("/")
    output, entries = {}, []
    analytics = ""
    endpoint = config.get("goatcounter_endpoint", "")
    if endpoint:
        parsed = urlsplit(endpoint)
        if parsed.scheme != "https" or not (parsed.hostname or "").endswith(".goatcounter.com") or parsed.path != "/count" or parsed.username or parsed.query or parsed.fragment:
            raise ValueError("Expected the public HTTPS GoatCounter /count endpoint, never a secret API token")
        analytics = f'<script data-goatcounter="{escape(endpoint, quote=True)}" async src="https://gc.zgo.at/count.js"></script>'

    def page(title, description, path, content, root="./", body_class="", extra_head=""):
        return template("layout", title=escape(title), description=escape(description, quote=True),
                        canonical=escape(f"{base}/{path}"), root=root, body_class=body_class,
                        og_type="article" if body_class == "article-page" else "website",
                        social_image=f"{base}/generation-vii/figures/00-cover.png",
                        content=content, extra_head=extra_head + analytics,
                        publications_current='aria-current="page"' if path == "" else "",
                        about_current='aria-current="page"' if path == "about.html" else "")

    slugs = set()
    publications = sorted(config["publications"], key=lambda item: item["published"], reverse=True)
    for entry in publications:
        slug = entry["slug"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in slugs:
            raise ValueError(f"Invalid or duplicate publication slug: {slug}")
        slugs.add(slug)
        source_path = (ROOT / entry["source"]).resolve()
        if not source_path.is_relative_to(ROOT):
            raise ValueError("Source must stay inside this repository")
        source = source_path.read_text(encoding="utf-8")
        body, deck, toc, minutes = render_markdown(source)
        published = date.fromisoformat(entry["published"])
        pretty_date = f"{published.day} {published.strftime('%B %Y')}"
        full_title = f'{entry["title"]}: {entry["subtitle"]}'
        comments = ""
        if entry.get("discussion_url") or config.get("giscus"):
            comments = '<section class="comments" id="comments" aria-labelledby="comments-title"><h2 id="comments-title">Discussion</h2><p>Questions, counterexamples, and alternative designs are welcome. A GitHub account is needed to comment.</p>'
            if entry.get("discussion_url"):
                comments += f'<p><a href="{escape(entry["discussion_url"], quote=True)}">Join the discussion on GitHub</a></p>'
            if config.get("giscus"):
                giscus = config["giscus"]
                attributes = {"repo": "MrQuality/articles", "repo-id": giscus["repo_id"], "category": giscus["category"], "category-id": giscus["category_id"], "mapping": "pathname", "strict": "1", "reactions-enabled": "1", "emit-metadata": "0", "input-position": "top", "theme": "preferred_color_scheme", "lang": "en", "loading": "lazy"}
                attrs = " ".join(f'data-{key}="{escape(value, quote=True)}"' for key, value in attributes.items())
                comments += f'<div class="giscus"></div><script src="https://giscus.app/client.js" {attrs} crossorigin="anonymous" async></script>'
            comments += "</section>"
        resources = f'<a href="{escape(posixpath.relpath(entry["source"], slug), quote=True)}">Markdown source</a>'
        if entry.get("experiments"):
            resources = f'<a href="{escape(posixpath.relpath(entry["experiments"], slug), quote=True)}/">Experiments &amp; results</a>' + resources
        if comments:
            resources += '<a href="#comments">Discussion</a>'
        content = template("article", type=escape(entry["type"]), article_title=escape(entry["title"]), subtitle=escape(entry["subtitle"]), deck=escape(deck), resources=resources,
                           published=entry["published"], date=pretty_date, minutes=minutes, slug=slug,
                           topics="".join(f"<li>{escape(topic)}</li>" for topic in entry["topics"]),
                           toc="".join(f'<li><a href="#{anchor}">{escape(title)}</a></li>' for anchor, title in toc), article_body=body, comments=comments)
        structured = {"@context": "https://schema.org", "@type": "Article", "headline": full_title, "description": entry["description"], "author": {"@type": "Person", "name": "Nir Rozen", "url": f"{base}/about.html"}, "datePublished": entry["published"], "mainEntityOfPage": f"{base}/{slug}/", "image": f'{base}/{entry["cover"]}'}
        extra = f'<meta name="giscus:backlink" content="{base}/{slug}/">' + '<script type="application/ld+json">' + json.dumps(structured, ensure_ascii=False).replace("<", "\\u003c") + "</script>"
        output[f"{slug}/index.html"] = page(f"{full_title} | Nir Rozen", entry["description"], f"{slug}/", content, "../", "article-page", extra)
        entry = dict(entry, minutes=minutes, pretty_date=pretty_date, full_title=full_title)
        entries.append(entry)

    cards = []
    for entry in entries:
        slug = entry["slug"]
        experiment_link = f'<a href="{escape(entry["experiments"], quote=True)}">Explore the experiments</a>' if entry.get("experiments") else ""
        cards.append(f'''<article class="publication">
  <div><p class="eyebrow">{escape(entry['type'])} / Free to read</p>
  <h3><a href="{slug}/">{escape(entry['title'])}<span>{escape(entry['subtitle'])}</span></a></h3>
  <p class="publication-summary">{escape(entry['description'])}</p>
  <p class="publication-meta"><time datetime="{entry['published']}">{entry['pretty_date']}</time> · {entry['minutes']} min read</p>
  <div class="publication-links"><a href="{slug}/">Read the essay</a>{experiment_link}</div></div>
  <a class="publication-image" href="{slug}/" aria-label="Read {escape(entry['full_title'], quote=True)}"><img src="{escape(entry['cover'], quote=True)}" alt="{escape(entry['cover_alt'], quote=True)}" width="1920" height="1080" decoding="async"></a>
</article>''')
    output["index.html"] = page(config["title"], config["description"], "", template("home", publications="\n".join(cards)), body_class="home-page")
    output["about.html"] = page("About Nir Rozen | Systems & Software", "Systems, performance, and quality engineering. The background and interests behind Nir Rozen’s technical writing.", "about.html", template("about"), body_class="about-page-body")
    # Preserve all existing experiment paths while applying the shared layout.
    experiment_source = (ROOT / "templates" / "experiments.html").read_text(encoding="utf-8")
    experiment_content = '<main id="main" class="wrap"><header class="article-header"><a class="back-link" href="../">Generation VII</a><p class="eyebrow">Companion material</p><h1>Experiments<br>&amp; results</h1></header><article class="prose experiments-prose">' + experiment_source + '</article></main>'
    output["generation-vii/experiments/index.html"] = page("Generation VII — Experiments & results | Nir Rozen", "Reproduce the resource-admission and concurrent-reservation models accompanying Generation VII.", "generation-vii/experiments/", experiment_content, "../../", "experiments-page")

    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    for key, value in [("title", config["title"]), ("link", base + "/"), ("description", config["description"]), ("language", "en")]:
        ET.SubElement(channel, key).text = value
    for entry in entries:
        item = ET.SubElement(channel, "item")
        link = f'{base}/{entry["slug"]}/'
        for key, value in [("title", entry["full_title"]), ("link", link), ("description", entry["description"]), ("pubDate", format_datetime(datetime.combine(date.fromisoformat(entry["published"]), datetime.min.time(), tzinfo=timezone.utc), usegmt=True))]:
            ET.SubElement(item, key).text = value
        ET.SubElement(item, "guid", {"isPermaLink": "true"}).text = link
    output["feed.xml"] = '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(rss, encoding="unicode") + "\n"
    sitemap = ET.Element("urlset", {"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"})
    for path in ["", "about.html"] + [f'{item["slug"]}/' for item in entries]:
        ET.SubElement(ET.SubElement(sitemap, "url"), "loc").text = f"{base}/{path}"
    output["sitemap.xml"] = '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(sitemap, encoding="unicode") + "\n"
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if committed HTML or feeds differ from their sources")
    args = parser.parse_args()
    stale = []
    for name, content in build().items():
        target = ROOT / name
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != content:
                stale.append(name)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")
    if stale:
        parser.exit(1, "Run python build.py to update: " + ", ".join(stale) + "\n")
    print("Publication site is current." if args.check else "Built publication pages, RSS, and sitemap.")


if __name__ == "__main__":
    main()
