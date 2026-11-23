"""Talk to the kcmd MCP server the way an agent would, and record what it returns.

Usage (repo root):  python3 tools/mcp_probe.py WORKSPACE OUT.md [ENTRY ...]
  WORKSPACE  a kcmd workspace folder (has catalog.yaml), e.g. results/03-studio/kcmd-okf
  ENTRY      entry names to look up (default: the first 2 from list-entries)
Read-only: it calls only initialize, tools/list, list-entries and lookup-entry.
It never calls modify-entry. Needs node on PATH (nvm use default).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KCMD = ROOT / "vendor/knowledge-catalog/toolbox/enrichment/node_modules/.bin/kcmd"
ws, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
wanted = sys.argv[3:]

proc = subprocess.Popen([str(KCMD), "mcp", "--path", str(ws)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, text=True, cwd=ws)
_id = 0


def rpc(method: str, params: dict | None = None, notify: bool = False):
    global _id
    msg = {"jsonrpc": "2.0", "method": method, "params": params or {}}
    if not notify:
        _id += 1
        msg["id"] = _id
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()
    if notify:
        return None
    while True:
        line = proc.stdout.readline()
        if not line:
            raise SystemExit("server closed: " + proc.stderr.read())
        r = json.loads(line)
        if r.get("id") == _id:
            return r


init = rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                          "clientInfo": {"name": "mcp-probe", "version": "0"}})
rpc("notifications/initialized", notify=True)
tools = rpc("tools/list")["result"]["tools"]
names = json.loads(rpc("tools/call", {"name": "list-entries", "arguments": {}})["result"]["content"][0]["text"])
lookups = {n: rpc("tools/call", {"name": "lookup-entry", "arguments": {"name": n}})["result"] for n in (wanted or names[:2])}
proc.terminate()

L = [f"# kcmd MCP probe: `{ws.relative_to(ROOT)}`", "",
     f"Server: `{init['result'].get('serverInfo')}`", "", "## tools/list", "",
     "| Tool | Description | Inputs |", "|---|---|---|"]
for t in tools:
    L.append(f"| `{t['name']}` | {t.get('description', '')} | `{', '.join(t.get('inputSchema', {}).get('properties', {}))}` |")
L += ["", f"## list-entries ({len(names)} entries)", "", "```json", json.dumps(names, indent=2), "```"]
for n, r in lookups.items():
    text = r["content"][0]["text"]
    L += ["", f"## lookup-entry `{n}`" + (" (error)" if r.get("isError") else ""), "",
          f"{len(text):,} characters returned.", "", "```json", text, "```"]
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"{len(tools)} tools, {len(names)} entries, looked up {list(lookups)}; wrote {out}")
