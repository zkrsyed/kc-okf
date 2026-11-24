"""Score the agent runs: run each final SQL and the golden SQL in BigQuery and compare the results.

Usage (from poc/05-agent):  uv run python -W ignore score.py
Reads results/05-agent/runs-*.jsonl, writes results/05-agent/scores.csv and results/05-agent/summary.md.

Rules (the same for every setup):
- No final ```sql block, or the final SQL fails  -> fail.
- must_not patterns (policy, e.g. geo.city for Tier C3) found in the final SQL -> fail.
- kind "scalar": a value in the first row of the agent's result is within 0.5 % of the golden value.
- kind "full":   same number of rows, and every golden row is matched by a different agent row
                 (each golden cell equals some cell of that agent row; numbers within 0.5 %).
- kind "topn":   the agent returns at least min(5, N) rows, and each of its first N rows matches a row of the
                 golden result extended by 10 rows (so ties at the cut-off don't fail it).
- A run passes if it passes against the golden SQL or any listed alternate (equally valid reading).
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import os
import re
from decimal import Decimal
from pathlib import Path

from google.cloud import bigquery

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / os.environ.get("KC_RUNS_DIR", "results/05-agent")  # KC_RUNS_DIR overrides (run 2)
bq = bigquery.Client(project="kc-okf-poc-261122")
CAP = bigquery.QueryJobConfig(maximum_bytes_billed=3 * 1024**3)
cache: dict[str, list[list]] = {}


def norm(v):
    if v is None:
        return None
    if isinstance(v, (int, float, Decimal)) and not isinstance(v, bool):
        return float(v)
    if isinstance(v, (dt.date, dt.datetime)):
        return v.isoformat()[:10]
    return str(v).strip().lower()


def run(sql: str, extra_limit: int = 0) -> list[list]:
    key = f"{sql}|{extra_limit}"
    if key not in cache:
        q = sql.strip().rstrip(";")
        if extra_limit:
            q = re.sub(r"LIMIT\s+(\d+)\s*$", lambda m: f"LIMIT {int(m.group(1)) + extra_limit}", q, flags=re.I)
        cache[key] = [[norm(v) for v in r.values()] for r in bq.query(q, job_config=CAP).result()]
    return cache[key]


def same(a, b) -> bool:
    if isinstance(a, float) and isinstance(b, float):
        return abs(a - b) <= max(0.005 * abs(a), 0.01)
    return a == b


def row_match(golden_row, agent_row) -> bool:
    return all(any(same(g, a) for a in agent_row) for g in golden_row)


def compare(kind: str, gold: list[list], gold_ext: list[list], got: list[list]) -> tuple[bool, str]:
    if kind == "scalar":
        g = gold[0][-1]
        ok = bool(got) and any(same(g, a) for a in got[0])
        return ok, f"golden {g}, agent first row {got[0][:4] if got else 'empty'}"
    if kind == "full":
        if len(got) != len(gold):
            return False, f"{len(got)} rows, golden {len(gold)}"
        free = list(range(len(got)))
        for gr in gold:
            hit = next((i for i in free if row_match(gr, got[i])), None)
            if hit is None:
                return False, f"golden row {gr} not found"
            free.remove(hit)
        return True, f"all {len(gold)} rows match"
    n = len(gold)
    if len(got) < min(5, n):
        return False, f"only {len(got)} rows, expected {n}"
    head = got[:n]
    miss = [r for r in head if not any(row_match(g, r) for g in gold_ext)]
    return not miss, ("top rows match" if not miss else f"{len(miss)} of top {len(head)} rows not in golden")


def main() -> None:
    qs = {q["id"]: q for q in json.load(open(Path(__file__).with_name("questions.json")))}
    rows = []
    for f in sorted(RES.glob("runs-*.jsonl")):
        for r in map(json.loads, f.open()):
            q = qs[r["id"]]
            sql = r.get("final_sql")
            verdict, note = False, ""
            policy_hits = [p for p in q.get("must_not", []) if sql and re.search(p, sql, re.I)]
            if not sql:
                note = "no final answer" + (f" ({r['error']})" if r.get("error") else "")
            elif policy_hits:
                note = f"policy broken: uses {', '.join(policy_hits)}"
            else:
                try:
                    got = run(sql)
                    for gsql in [q["golden_sql"]] + q.get("alternates", []):
                        ok, note = compare(q["kind"], run(gsql), run(gsql, 10) if q["kind"] == "topn" else [], got)
                        if ok:
                            verdict = True
                            break
                except Exception as e:  # noqa: BLE001
                    note = f"final SQL failed: {str(e)[:150]}"
            rows.append({"setup": r["setup"], "run": r.get("run", 1), "id": r["id"], "pass": int(verdict), "note": note,
                         "partition_filter": int(bool(sql and re.search(r"event_date_dt", sql))),
                         "tool_calls": r["n_tool_calls"], "context_reads": sum(c["name"] in ("read_file", "list_files", "lookup-entry", "list-entries") for c in r["tool_calls"]),
                         "queries": r["queries"], "gb_billed": round(r["bytes_billed"] / 1e9, 3),
                         "input_tokens": r["input_tokens"], "output_tokens": r["output_tokens"], "seconds": r["seconds"]})
    rows.sort(key=lambda x: (x["setup"], x["run"], x["id"]))
    with open(RES / "scores.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    names = {"A": "A: no context", "B": "B: KC context as OKF files", "C": "C: KC context via kcmd MCP",
             "B2": "B2: run 2 context as OKF files", "C2": "C2: run 2 context via kcmd MCP"}
    setups = sorted({r["setup"] for r in rows})
    L = ["| Setup | Pass | Held-out (13-15) | Partition filter | Avg tool calls | Avg context reads | Avg input tokens | Avg seconds | GB billed |", "|---|---|---|---|---|---|---|---|---|"]
    for s in setups:
        rs = [r for r in rows if r["setup"] == s]
        ho = [r for r in rs if r["id"] >= 13]
        avg = lambda k: sum(r[k] for r in rs) / len(rs)  # noqa: E731
        L.append(f"| {names.get(s, s)} | **{sum(r['pass'] for r in rs)}/{len(rs)}** | {sum(r['pass'] for r in ho)}/{len(ho)} | "
                 f"{sum(r['partition_filter'] for r in rs)}/{len(rs)} | {avg('tool_calls'):.1f} | {avg('context_reads'):.1f} | "
                 f"{avg('input_tokens'):,.0f} | {avg('seconds'):.0f} | {sum(r['gb_billed'] for r in rs):.2f} |")
    L += ["", "| Q | Question | " + " | ".join(names.get(s, s) for s in setups) + " |", "|---|---|" + "---|" * len(setups)]
    for i, q in qs.items():
        cells = []
        for s in setups:
            r = next((x for x in rows if x["setup"] == s and x["id"] == i), None)
            cells.append("–" if not r else ("✅ pass" if r["pass"] else f"❌ {r['note'][:70]}"))
        L.append(f"| {i}{'*' if not q.get('seen_by_studio', True) else ''} | {q['question']} | " + " | ".join(cells) + " |")
    L += ["", "\\* held-out question: not in Studio's eval set, so Studio never optimised for it."]
    (RES / "summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
