# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown==3.7"]
# ///
"""Build report.html: one readable page from the repo's markdown and SVG files.

Run from the repo root:  uv run tools/build_report.py
The markdown files stay the source of truth; report.html is regenerated from them.
"""
from __future__ import annotations

import base64
import datetime as dt
import html
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent

# (section id, title, markdown file) in reading order
SECTIONS: list[tuple[str, str, str]] = [
    ("start", "Start here", "docs/start-here.md"),
    ("concepts", "Concepts in plain words", "docs/concepts.md"),
    ("step-0", "Step 0 · Setup", "results/00-setup.md"),
    ("step-0-cmds", "Step 0 · commands", "poc/00-setup/README.md"),
    ("step-1", "Step 1 · Inspect the catalog", "results/01-inspect.md"),
    ("step-1-cmds", "Step 1 · commands", "poc/01-inspect/README.md"),
    ("step-2", "Step 2 · kcagent (sample agent)", "results/02-kcagent.md"),
    ("step-2-how", "Step 2 · how kcagent and its MCP server work", "docs/kcagent-how-it-works.md"),
    ("step-2-cmds", "Step 2 · commands", "poc/02-kcagent/README.md"),
    ("step-3", "Step 3 · Knowledge Studio", "results/03-studio.md"),
    ("step-3-cmds", "Step 3 · commands", "poc/03-studio/README.md"),
    ("context-layer", "Where OKF fits: serving context to your agents", "docs/context-layer.md"),
    ("step-4", "Step 4 · OKF and playbooks", "results/04-okf.md"),
    ("step-4-cmds", "Step 4 · commands", "poc/04-okf/README.md"),
    ("step-5", "Step 5 · Agent test", "results/05-agent.md"),
    ("step-5-cmds", "Step 5 · commands", "poc/05-agent/README.md"),
    ("step-6", "Step 6 · Verdict", "results/06-verdict.md"),
    ("step-7", "Step 7 · Studio run 2 (custom instruction)", "results/07-studio-run2.md"),
    ("step-7-cmds", "Step 7 · commands", "poc/07-studio-run2/README.md"),
    ("agents", "For AI agents: facts, IDs, file map", "AGENTS.md"),
    ("resources", "Cloud resources and clean-up", "results/cloud-resources.md"),
]
# Later steps are picked up automatically when their files exist.
OPTIONAL = [
    ("step-{n}", "Step {n}: results", "results/0{n}-*.md"),
    ("step-{n}-cmds", "Step {n}: commands", "poc/0{n}-*/README.md"),
]

FILE_TO_ID = {path: sid for sid, _, path in SECTIONS}


def collect_sections() -> list[tuple[str, str, Path]]:
    out = [(sid, title, ROOT / p) for sid, title, p in SECTIONS if (ROOT / p).exists()]
    known = {p for _, _, p in out}
    for n in range(3, 10):
        for sid_t, title_t, glob_t in OPTIONAL:
            for p in sorted(ROOT.glob(glob_t.format(n=n))):
                if p not in known and p.name != "cloud-resources.md":
                    first = p.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
                    out.insert(-1, (sid_t.format(n=n), first or title_t.format(n=n), p))
                    known.add(p)
                    FILE_TO_ID[str(p.relative_to(ROOT))] = sid_t.format(n=n)
    return out


def inline_svgs(md_text: str, base: Path) -> str:
    """Replace ![alt](x.svg) with the SVG markup itself, so diagrams render inside the page."""

    def repl(m: re.Match) -> str:
        svg_path = (base / m.group(2)).resolve()
        if not svg_path.exists():
            return m.group(0)
        svg = svg_path.read_text(encoding="utf-8")
        svg = re.sub(r"<\?xml[^>]*\?>", "", svg).strip()
        return f'\n<figure class="diagram">{svg}<figcaption>{html.escape(m.group(1))}</figcaption></figure>\n'

    return re.sub(r"!\[([^\]]*)\]\(([^)\s]+\.svg)\)", repl, md_text)


MIME = {".png": "image/png", ".webp": "image/webp", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}


def inline_images(md_text: str, base: Path) -> str:
    """Embed screenshots as data URIs so report.html is one self-contained file. Click to enlarge."""

    def repl(m: re.Match) -> str:
        img_path = (base / m.group(2)).resolve()
        if not img_path.exists():
            return m.group(0)
        data = base64.b64encode(img_path.read_bytes()).decode()
        alt = html.escape(m.group(1))
        return (f'\n<figure class="shot"><img loading="lazy" alt="{alt}" '
                f'src="data:{MIME[img_path.suffix.lower()]};base64,{data}"><figcaption>{alt}</figcaption></figure>\n')

    return re.sub(r"!\[([^\]]*)\]\(([^)\s]+\.(?:png|webp|jpe?g))\)", repl, md_text, flags=re.I)


def fix_links(body: str, src: Path) -> str:
    """Point links at sections of this page where possible, else at repo-relative paths."""

    def repl(m: re.Match) -> str:
        href = m.group(1)
        if re.match(r"^(https?:|mailto:|#)", href):
            return m.group(0)
        path, _, frag = href.partition("#")
        target = (src.parent / path).resolve()
        try:
            rel = str(target.relative_to(ROOT))
        except ValueError:
            return m.group(0)
        if rel in FILE_TO_ID:
            return f'href="#{FILE_TO_ID[rel]}"'
        return f'href="{rel}{"#" + frag if frag else ""}"'

    return re.sub(r'href="([^"]+)"', repl, body)


def render(sid: str, path: Path) -> str:
    text = inline_images(inline_svgs(path.read_text(encoding="utf-8"), path.parent), path.parent)
    # let markdown inside <details> blocks render (GitHub does this implicitly)
    text = re.sub(r"<details>", '<details markdown="1">', text)
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "md_in_html", "toc", "sane_lists"],
        extension_configs={"toc": {"slugify": lambda v, s: sid + "-" + re.sub(r"[^\w]+", "-", v.lower()).strip("-")}},
    )
    body = md.convert(text)
    body = fix_links(body, path)
    # wrap wide tables so they scroll instead of breaking the page
    body = body.replace("<table>", '<div class="tablewrap"><table>').replace("</table>", "</table></div>")
    # verified / docs / guess badges
    for word, cls in (("verified", "ok"), ("docs", "doc"), ("guess", "guess")):
        body = re.sub(rf"<strong>{word}</strong>", f'<span class="badge {cls}">{word}</span>', body)
    return body


CSS = """
:root{--bg:#ffffff;--fg:#1f2328;--muted:#59636e;--line:#d1d9e0;--panel:#f6f8fa;--accent:#0b57d0;--code:#eff1f3;
--ok:#1a7f37;--doc:#0b57d0;--guess:#9a6700}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#0d1117;--fg:#e6edf3;--muted:#9198a1;--line:#30363d;--panel:#161b22;--accent:#6ea8fe;--code:#1f242c;--ok:#3fb950;--doc:#6ea8fe;--guess:#d29922}}
:root[data-theme="dark"]{--bg:#0d1117;--fg:#e6edf3;--muted:#9198a1;--line:#30363d;--panel:#161b22;--accent:#6ea8fe;--code:#1f242c;--ok:#3fb950;--doc:#6ea8fe;--guess:#d29922}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
a{color:var(--accent)}
.layout{display:grid;grid-template-columns:280px 1fr;min-height:100vh}
nav{position:sticky;top:0;height:100vh;overflow:auto;border-right:1px solid var(--line);background:var(--panel);padding:20px 16px}
nav h1{font-size:16px;margin:0 0 4px}
nav .meta{font-size:12px;color:var(--muted);margin-bottom:16px}
nav ol{list-style:none;padding:0;margin:0}
nav li a{display:block;padding:6px 8px;border-radius:6px;text-decoration:none;color:var(--fg);font-size:14px}
nav li a:hover{background:var(--line)}
main{padding:24px 40px 80px;max-width:1100px;min-width:0}
section{border-bottom:1px solid var(--line);padding-bottom:32px;margin-bottom:32px}
.src{font-size:12px;color:var(--muted);margin-bottom:8px}
h1,h2,h3,h4{line-height:1.3}
main h1{font-size:28px;margin-top:8px}
code{background:var(--code);padding:2px 5px;border-radius:4px;font-size:90%}
pre{background:var(--code);padding:12px 14px;border-radius:8px;overflow:auto}
pre code{padding:0;background:none}
.tablewrap{overflow-x:auto;margin:12px 0}
table{border-collapse:collapse;font-size:14px}
th,td{border:1px solid var(--line);padding:6px 10px;vertical-align:top;text-align:left}
th{background:var(--panel)}
details{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:8px 14px;margin:12px 0}
summary{cursor:pointer;font-weight:600}
figure.diagram{margin:16px 0;background:#fff;border:1px solid var(--line);border-radius:8px;padding:8px;overflow-x:auto}
figure.diagram svg{max-width:100%;height:auto;display:block}
figcaption{font-size:13px;color:#59636e;padding:4px 4px 0}
figure.shot{margin:16px 0;border:1px solid var(--line);border-radius:8px;padding:8px;background:var(--panel)}
figure.shot img{display:block;max-width:min(100%,720px);height:auto;border-radius:4px;cursor:zoom-in}
figure.shot.big img{max-width:100%;cursor:zoom-out}
figure.shot figcaption{color:var(--muted)}
nav li.grp{margin:14px 8px 4px;font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
nav li.sub a{padding-left:20px;font-size:13px;color:var(--muted)}
details.cmds{background:var(--bg)}
details.cmds>summary{font-size:15px}
pre{position:relative}
.copybtn{position:absolute;top:6px;right:6px;font-size:11px;padding:2px 6px;border:1px solid var(--line);border-radius:4px;background:var(--panel);color:var(--fg);cursor:pointer;opacity:.7}
.copybtn:hover{opacity:1}
main section>h1:first-of-type{border-bottom:2px solid var(--accent);padding-bottom:6px}
.badge{display:inline-block;font-size:12px;font-weight:600;padding:0 6px;border-radius:10px;border:1px solid currentColor}
.badge.ok{color:var(--ok)}.badge.doc{color:var(--doc)}.badge.guess{color:var(--guess)}
.themebtn{margin-top:16px;font-size:12px;background:none;border:1px solid var(--line);color:var(--fg);border-radius:6px;padding:4px 8px;cursor:pointer}
@media (max-width:860px){.layout{grid-template-columns:1fr}nav{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line)}main{padding:16px}}
"""

JS = """
document.querySelectorAll('figure.shot img').forEach(i=>i.onclick=()=>i.parentElement.classList.toggle('big'));
document.querySelectorAll('pre').forEach(p=>{const b=document.createElement('button');b.className='copybtn';b.textContent='copy';b.onclick=()=>{navigator.clipboard&&navigator.clipboard.writeText(p.innerText.replace(/copy$/,'').trim());b.textContent='copied';setTimeout(()=>b.textContent='copy',1200)};p.appendChild(b)});
const b=document.getElementById('themebtn');
b.onclick=()=>{const r=document.documentElement;const dark=r.dataset.theme?r.dataset.theme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;r.dataset.theme=dark?'light':'dark';};
"""


GROUPS = [("Orientation", ("start", "concepts")), ("The steps", ("step-", "context-layer")), ("Reference", ("agents", "resources"))]


def group_of(sid: str) -> str:
    for name, prefixes in GROUPS:
        if any(sid == p or (p.endswith("-") and sid.startswith(p)) for p in prefixes):
            return name
    return "Reference"


def main() -> None:
    sections = collect_sections()
    nav_parts, last = [], None
    for sid, t, _ in sections:
        g = group_of(sid)
        if g != last:
            nav_parts.append(f'<li class="grp">{html.escape(g)}</li>')
            last = g
        cls = ' class="sub"' if sid.endswith(("-cmds", "-how")) else ""
        nav_parts.append(f'<li{cls}><a href="#{sid}">{html.escape(t)}</a></li>')
    nav = "\n".join(nav_parts)

    def wrap(sid: str, p: Path) -> str:
        inner = render(sid, p)
        if sid.endswith("-cmds"):
            inner = f'<details class="cmds"><summary>Commands to repeat this step ({html.escape(str(p.relative_to(ROOT)))})</summary>{inner}</details>'
        return (f'<section id="{sid}"><div class="src">Source: <a href="{p.relative_to(ROOT)}">{p.relative_to(ROOT)}</a>'
                f' · <a href="#top">back to top</a></div>\n{inner}</section>')

    body = "\n".join(wrap(sid, p) for sid, _, p in sections)
    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>KC Studio OKF POC</title><style>{CSS}</style></head>
<body id="top"><div class="layout">
<nav><h1>Knowledge Catalog, Studio &amp; OKF POC</h1><div class="meta">Generated {stamp} from the repo's markdown. Edit the .md files, then run <code>uv run tools/build_report.py</code>.</div>
<ol>{nav}</ol><button class="themebtn" id="themebtn">Toggle light / dark</button></nav>
<main>{body}</main></div><script>{JS}</script></body></html>
"""
    (ROOT / "report.html").write_text(page, encoding="utf-8")
    print(f"wrote report.html: {len(sections)} sections, {len(page)//1024} KB")


if __name__ == "__main__":
    main()
