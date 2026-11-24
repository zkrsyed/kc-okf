"""Read-only snapshot of a context set and the structured metadata around it.

Writes, under OUT_DIR:
  entries/<entry-id>.json   every entry in the context set, full view (all aspects)
  entry-links.json          entry links found for the context set's entries
  glossaries.json           glossaries (with categories and terms) in us and global
  bigquery-entry.json       the real @bigquery entry for the events table
  summary.md                counts: entry types, aspect types, schema slots, column descriptions

Usage: python3 tools/dump_context_set.py <context-set-id> <out-dir>
Needs: gcloud logged in (CLOUDSDK_ACTIVE_CONFIG_NAME=kc-okf). Only GET/lookup calls.
"""
import json
import pathlib
import subprocess
import sys
import urllib.parse
import urllib.request
from collections import Counter

PROJECT = "kc-okf-poc-261122"
LOC = "us"
API = "https://dataplex.googleapis.com/v1"
TABLE = f"bigquery.googleapis.com/projects/{PROJECT}/datasets/ga4_sample/tables/events"

TOKEN = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()


def get(url, params=None):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}", "x-goog-user-project": PROJECT})
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_body": e.read().decode()[:500]}


def paged(url, key, params=None):
    params = dict(params or {})
    out = []
    while True:
        d = get(url, params)
        if "_error" in d:
            return d
        out += d.get(key, [])
        if not d.get("nextPageToken"):
            return out
        params["pageToken"] = d["nextPageToken"]


def walk_fields(fields, prefix=""):
    """Yield (path, description) for a schema aspect's field list, nested included."""
    for f in fields or []:
        name = f.get("name", "?")
        path = prefix + name
        yield path, f.get("description", "")
        yield from walk_fields(f.get("fields"), path + ".")


def main(cs, out):
    out = pathlib.Path(out)
    (out / "entries").mkdir(parents=True, exist_ok=True)
    base = f"{API}/projects/{PROJECT}/locations/{LOC}"

    entries = paged(f"{base}/entryGroups/{cs}/entries", "entries", {"pageSize": 200})
    if isinstance(entries, dict):
        sys.exit(f"list failed: {entries}")
    full = []
    for e in entries:
        d = get(f"{API}/{e['name']}", {"view": "ALL"})
        full.append(d)
        fn = e["name"].split("/entries/")[1].replace("/", "__") + ".json"
        (out / "entries" / fn).write_text(json.dumps(d, indent=2))

    # entry links pointing at / from each entry
    links = {}
    for d in full:
        r = get(f"{base}:lookupEntryLinks", {"entry": d["name"]})
        if r.get("entryLinks"):
            links[d["name"]] = r["entryLinks"]
    (out / "entry-links.json").write_text(json.dumps(links, indent=2))

    gl = {}
    for L in ("us", "global"):
        gs = paged(f"{API}/projects/{PROJECT}/locations/{L}/glossaries", "glossaries")
        if isinstance(gs, list):
            for g in gs:
                g["terms"] = paged(f"{API}/{g['name']}/terms", "terms")
                g["categories"] = paged(f"{API}/{g['name']}/categories", "categories")
        gl[L] = gs
    (out / "glossaries.json").write_text(json.dumps(gl, indent=2))

    bq = get(f"{base}:lookupEntry", {"entry": f"projects/{PROJECT}/locations/{LOC}/entryGroups/@bigquery/entries/{TABLE}", "view": "ALL"})
    (out / "bigquery-entry.json").write_text(json.dumps(bq, indent=2))

    # summary
    types = Counter()
    aspects = Counter()
    lines = [f"# Snapshot of context set `{cs}`", ""]
    schema_rows = []
    for d in full:
        dt = d.get("aspects", {})
        doc_type = next((v["data"].get("type") for k, v in dt.items() if k.endswith(".document")), "?")
        types[doc_type] += 1
        for k, v in dt.items():
            aspects[k.split(".", 1)[1]] += 1
            if k.endswith(".schema"):
                for p, desc in walk_fields(v.get("data", {}).get("fields")):
                    schema_rows.append((d["name"].split("/entries/")[1], p, desc))
    lines += [f"- entries: {len(full)}", f"- document types: {dict(types)}", f"- aspect types: {dict(aspects)}"]
    nlinks = sum(len(v) for v in links.values())
    ltypes = Counter(l.get("entryLinkType", "?").split("/")[-1] for v in links.values() for l in v)
    lines.append(f"- entry links (lookupEntryLinks over all entries, duplicates possible): {nlinks} {dict(ltypes)}")
    gterms = {L: (sum(len(g.get('terms') or []) for g in v) if isinstance(v, list) else v) for L, v in gl.items()}
    lines.append(f"- glossaries: us={len(gl['us']) if isinstance(gl['us'], list) else gl['us']}, global={len(gl['global']) if isinstance(gl['global'], list) else gl['global']}; terms {gterms}")
    with_desc = [r for r in schema_rows if r[2]]
    lines.append(f"- schema aspects inside the context set: {len(schema_rows)} field slots, {len(with_desc)} with a description")

    bqa = bq.get("aspects", {})
    bq_schema = next((v for k, v in bqa.items() if k.endswith(".schema")), None)
    if bq_schema:
        rows = list(walk_fields(bq_schema.get("data", {}).get("fields")))
        top = [r for r in rows if "." not in r[0]]
        lines.append(f"- @bigquery events entry: {sum(1 for r in top if r[1])} of {len(top)} columns described; "
                     f"{sum(1 for r in rows if r[1])} of {len(rows)} field paths described")
    lines.append(f"- @bigquery events entry aspects: {sorted(k.split('.', 1)[1] for k in bqa)}")
    overview = next((v for k, v in bqa.items() if k.endswith(".overview")), None)
    if overview:
        lines.append(f"- @bigquery overview starts: {overview.get('data', {}).get('content', '')[:120]!r}")
    if with_desc:
        lines += ["", "## Field descriptions found in context-set schema aspects", "", "| entry | field | description |", "|---|---|---|"]
        lines += [f"| {e} | `{p}` | {d.replace('|', '/')} |" for e, p, d in with_desc]
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:12]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
