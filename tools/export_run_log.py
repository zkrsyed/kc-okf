"""Export a Knowledge Studio enrichment run's event log from Cloud Logging.

Usage (repo root, gcloud profile kc-okf active):
    python3 tools/export_run_log.py RUN_ID OUT_PREFIX
Writes OUT_PREFIX.jsonl (raw entries) and OUT_PREFIX.md (readable timeline).
Read-only: it only calls `gcloud logging read`.
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

run_id, prefix = sys.argv[1], Path(sys.argv[2])
flt = (
    'logName="projects/kc-okf-poc-261122/logs/dataplex.googleapis.com%2Fagent_task" '
    f'AND jsonPayload.runMetadata.agentRun:"{run_id}"'
)
raw = subprocess.run(
    ["gcloud", "logging", "read", flt, "--freshness=30d", "--limit=5000", "--order=asc", "--format=json"],
    check=True, capture_output=True, text=True,
).stdout
entries = json.loads(raw)
entries.sort(key=lambda e: (e["timestamp"], e.get("insertId", "")))

prefix.parent.mkdir(parents=True, exist_ok=True)
with open(prefix.with_suffix(".jsonl"), "w", encoding="utf-8") as f:
    for e in entries:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")

sev = Counter(e.get("severity", "") for e in entries)
types = Counter(e["jsonPayload"].get("eventType", "") for e in entries)
states = [e["jsonPayload"].get("runMetadata", {}).get("state", "") for e in entries]
lines = [
    f"# Run log: `{run_id}`",
    "",
    f"Exported from Cloud Logging (`dataplex.googleapis.com/agent_task`), {len(entries)} entries, "
    f"{entries[0]['timestamp'][:19] if entries else '-'} to {entries[-1]['timestamp'][:19] if entries else '-'} UTC. "
    f"Last run state seen: **{states[-1] if states else '-'}**.",
    "",
    "Severity counts: " + ", ".join(f"{k or 'none'} {v}" for k, v in sev.most_common()),
    "",
    "Event types: " + ", ".join(f"{k or 'none'} {v}" for k, v in types.most_common()),
    "",
    "| Time (UTC) | Sev | Message |",
    "|---|---|---|",
]
for e in entries:
    p = e["jsonPayload"]
    msg = p.get("message") or json.dumps({k: v for k, v in p.items() if k not in ("@type", "agentTask", "runMetadata")})
    msg = " ".join(str(msg).split()).replace("|", "\\|")
    lines.append(f"| {e['timestamp'][11:19]} | {e.get('severity', '')[:4]} | {msg} |")
prefix.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"{len(entries)} entries; last state {states[-1] if states else '-'}; wrote {prefix}.jsonl and .md")
