# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml==6.0.2"]
# ///
"""Check an OKF bundle against the main rules of OKF v0.3 (SPEC.md in open-knowledge-format/open-knowledge-format).

Usage:  uv run tools/okf_check.py BUNDLE_DIR [OUT.md]
Read-only. Reports, per .md file: whether the frontmatter parses, `type`, `title`, `description`,
the trust fields (`generated`, `verified`, `sources`), extension keys, and the citation style in the body.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

root = Path(sys.argv[1])
rows, notes = [], []
for p in sorted(root.rglob("*.md")):
    rel = p.relative_to(root)
    if any(part.startswith(".") for part in rel.parts):
        continue
    text = p.read_text(encoding="utf-8")
    fm, body, ok = {}, text, "no frontmatter"
    if text.startswith("---\n"):
        try:
            head, body = text[4:].split("\n---\n", 1)
            fm = yaml.safe_load(head) or {}
            ok = "yes" if isinstance(fm, dict) else "not a mapping"
        except Exception as e:  # noqa: BLE001
            ok = f"error: {e}"
    reserved = p.name in ("index.md", "log.md")
    concept = (not reserved) and isinstance(fm, dict) and bool(fm.get("type"))
    ext = sorted(k for k in fm if isinstance(k, str) and k.startswith("x-")) if isinstance(fm, dict) else []
    cites = "footnotes" if re.search(r"\[\^[\w-]+\]", body) else ("numbered [n] list" if re.search(r"\[\d+(, ?\d+)*\]", body) else "none")
    rows.append((str(rel), ok, fm.get("type", "") if isinstance(fm, dict) else "", "yes" if fm.get("title") else "no",
                 "yes" if fm.get("description") else "no",
                 ",".join(k for k in ("generated", "verified", "sources") if fm.get(k)) or "none", ",".join(ext) or "none", cites,
                 "reserved" if reserved else ("concept" if concept else "skipped")))

has_root_index = (root / "index.md").exists()
okf_version = None
if has_root_index:
    t = (root / "index.md").read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", t, re.S)
    okf_version = (yaml.safe_load(m.group(1)) or {}).get("okf_version") if m else None

L = [f"# OKF v0.3 check: `{root}`", "",
     f"- Root `index.md`: {'yes' if has_root_index else 'no'}; `okf_version`: {okf_version or 'not declared'}",
     f"- Files: {len(rows)}; concepts: {sum(r[-1] == 'concept' for r in rows)}; frontmatter errors: {sum(r[1].startswith("error") or r[1] == "not a mapping" for r in rows)}",
     "- Conformance (§11.1) only needs parseable frontmatter and valid reserved files, so a bundle can be conformant while missing every optional field.",
     "", "| File | Frontmatter parses | type | title | description | trust fields | x- keys | citations | role |", "|---|---|---|---|---|---|---|---|---|"]
L += ["| " + " | ".join(f"`{r[0]}`" if i == 0 else r[i] for i in range(len(r))) + " |" for r in rows]
out = "\n".join(L) + "\n"
if len(sys.argv) > 2:
    Path(sys.argv[2]).write_text(out, encoding="utf-8")
print(out)
