"""Run every question once in one setup, appending to results/05-agent/runs-<SETUP>.jsonl (resumable).

Usage (from poc/05-agent):  uv run python -W ignore run_all.py SETUP [RUN]
Run the three setups as three parallel processes; each process runs its questions one at a time.
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

from agent import ROOT, run_one

setup = sys.argv[1]
run = int(sys.argv[2]) if len(sys.argv) > 2 else 1
out = ROOT / f"results/05-agent/runs-{setup}.jsonl"
out.parent.mkdir(parents=True, exist_ok=True)
done = {(r["id"], r.get("run", 1)) for r in map(json.loads, out.open())} if out.exists() else set()
questions = json.load(open(Path(__file__).with_name("questions.json")))


async def main() -> None:
    for q in questions:
        if (q["id"], run) in done:
            continue
        for attempt in range(4):
            r = await run_one(setup, q)
            if r["error"] and ("429" in r["error"] or "RESOURCE_EXHAUSTED" in r["error"]):
                time.sleep(30 * (attempt + 1))  # quota: back off and retry the same question
                continue
            break
        r["run"] = run
        with out.open("a") as f:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"{setup} q{q['id']:>2} calls={r['n_tool_calls']:>2} sql={'yes' if r['final_sql'] else 'NO '} {r['seconds']}s {r['error'] or ''}", flush=True)


asyncio.run(main())
