"""Read-through checks for report.html (no browser needed).

Usage: python3 tools/check_report.py [--text OUT.txt]
Checks: in-page anchors resolve, images are embedded, no raw Markdown left (image syntax, **bold**, pipe tables,
unclosed code fences), repo-relative links point to files that exist, no private strings.
With --text, also writes the visible text of the page for reading.
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
page = (ROOT / "report.html").read_text(encoding="utf-8")


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.hrefs, self.imgs, self.text, self.skip = set(), [], [], [], 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "href" in a:
            self.hrefs.append(a["href"])
        if tag == "img":
            self.imgs.append(a.get("src", "")[:40])
        if tag in ("script", "style", "svg"):
            self.skip += 1
        if tag in ("p", "li", "h1", "h2", "h3", "h4", "tr", "pre", "figcaption", "summary", "br"):
            self.text.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "svg"):
            self.skip -= 1
        if tag in ("td", "th"):
            self.text.append(" | ")

    def handle_data(self, d):
        if not self.skip:
            self.text.append(d)


p = P()
p.feed(page)
problems = []
for h in p.hrefs:
    if h.startswith("#") and h[1:] and h[1:] not in p.ids:
        problems.append(f"broken anchor {h}")
    elif not re.match(r"^(https?:|mailto:|#)", h):
        target = ROOT / h.split("#")[0]
        if h.split("#")[0] and not target.exists():
            problems.append(f"repo link to missing file {h}")
non_data = [s for s in p.imgs if not s.startswith("data:")]
if non_data:
    problems.append(f"{len(non_data)} images not embedded: {non_data[:3]}")
text = "".join(p.text)
for pat, what in ((r"!\[[^\]]*\]\(", "raw image markdown"), (r"(?<![`*])\*\*[A-Za-z][^*\n]{0,60}\*\*(?![`*])", "raw **bold**"),
                  (r"^\s*\|[-: |]+\|\s*$", "raw table separator"), (r"```", "raw code fence")):
    for m in re.finditer(pat, text, re.M):
        problems.append(f"{what}: ...{text[max(0, m.start() - 40):m.end() + 20]!r}")
# private strings to look for live in a git-ignored file, so the checker itself doesn't publish them
private = ROOT / ".private-strings"
for secret in (private.read_text().split() if private.exists() else []):
    if secret.lower() in page.lower():
        problems.append(f"private string present: {secret}")
print(f"{len(p.imgs)} images, {len(p.hrefs)} links, {len(p.ids)} ids, {len(text):,} chars of text")
print("\n".join(problems) if problems else "no problems found")
if "--text" in sys.argv:
    Path(sys.argv[sys.argv.index("--text") + 1]).write_text(re.sub(r"\n\s*\n+", "\n\n", text), encoding="utf-8")
