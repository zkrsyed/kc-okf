"""A small LangGraph NL-to-SQL agent, run in three context setups (step 5 of the POC).

Setups (the only difference is how the agent can read Knowledge Catalog context):
  A  none   - schema tool + SQL tool only
  B  files  - A + read the OKF bundle that `kcmd pull --format okf` wrote (list_files / read_file)
  C  mcp    - A + the `kcmd mcp` server on the same bundle (list-entries / lookup-entry; modify-entry removed)

Usage (from poc/05-agent):  uv run python agent.py SETUP QUESTION_ID [RUN]
Library use: `await run_one(setup, question)` returns a dict with the final SQL, answer, tool calls, tokens and timing.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path

from google.cloud import bigquery
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent  # deprecated alias in LangGraph 1.x, still supported

ROOT = Path(__file__).resolve().parents[2]
PROJECT = "kc-okf-poc-261122"
TABLE = f"{PROJECT}.ga4_sample.events"
MODEL = "gemini-3.5-flash"          # Vertex AI, location global (the only one that served it in this project)
BUNDLE_WS = Path(os.environ.get("KC_BUNDLE", ROOT / "results/04-okf/pull-after-push"))  # published context set as OKF (step 4); KC_BUNDLE overrides (run 2)
KCMD = ROOT / "vendor/knowledge-catalog/toolbox/enrichment/node_modules/.bin/kcmd"
MAX_BYTES = 3 * 1024**3             # per-query cap: a query that would scan more fails instead of costing more
RECURSION_LIMIT = 60   # about 30 tool calls

bq = bigquery.Client(project=PROJECT)
stats = {"bytes": 0, "queries": 0}


@tool
def get_table_schema() -> str:
    """Return every column path and data type of the events table (nested fields as a.b.c)."""
    rows = bq.query(
        "SELECT field_path, data_type FROM `kc-okf-poc-261122.ga4_sample.INFORMATION_SCHEMA.COLUMN_FIELD_PATHS` "
        "WHERE table_name = 'events' ORDER BY field_path"
    ).result()
    return f"Table `{TABLE}`\n" + "\n".join(f"{r.field_path}: {r.data_type.split('<')[0]}" for r in rows)


@tool
def run_sql(sql: str) -> str:
    """Run a BigQuery Standard SQL query and return up to 25 rows. Queries scanning over 3 GB are refused."""
    try:
        job = bq.query(sql, job_config=bigquery.QueryJobConfig(maximum_bytes_billed=MAX_BYTES))
        it = job.result(max_results=25)
        rows = list(it)
        stats["bytes"] += job.total_bytes_billed or 0
        stats["queries"] += 1
        cols = [f.name for f in (it.schema or [])]
        body = "\n".join(" | ".join(str(v) for v in r.values()) for r in rows)
        return f"{it.total_rows} rows; columns: {', '.join(cols)}\n{body}"
    except Exception as e:  # noqa: BLE001 - the agent should see the error and fix its query
        return f"ERROR: {str(e)[:600]}"


def file_tools(bundle: Path):
    @tool
    def list_files(folder: str = "") -> str:
        """List the files and folders of the knowledge bundle (paths relative to the bundle root)."""
        base = (bundle / folder).resolve()
        if not str(base).startswith(str(bundle.resolve())) or not base.is_dir():
            return "ERROR: not a folder in the bundle"
        return "\n".join(sorted(str(p.relative_to(bundle)) + ("/" if p.is_dir() else "") for p in base.iterdir()))

    @tool
    def read_file(path: str) -> str:
        """Read one Markdown file of the knowledge bundle, e.g. agents.md or documents/foo.md."""
        p = (bundle / path).resolve()
        if not str(p).startswith(str(bundle.resolve())) or not p.is_file():
            return "ERROR: no such file in the bundle"
        return p.read_text(encoding="utf-8")

    return [list_files, read_file]


BASE_PROMPT = f"""You are a data analyst agent. You answer questions about the BigQuery table `{TABLE}`
(Google Analytics 4 e-commerce events from the Google Merchandise Store, one row per event).
Use the tools to understand the data, then run your final query with run_sql and check the result.
Be efficient: once a query returns a result you have checked, stop exploring and answer.
End with a short answer and the exact final query in one ```sql code block."""

CONTEXT_PROMPT = {
    "A": "",
    "B": """
A knowledge bundle (reviewed context pages for this table) is available through list_files and read_file.
Before writing SQL, read agents.md (the root index), then follow the index pages to the pages that matter.
The bundle's rules and metric definitions are company policy: follow them, and say when a rule changes the question.""",
    "C": """
A knowledge base (reviewed context pages for this table) is available through the tools list-entries and lookup-entry.
Before writing SQL, look up the entry `agents` (the root index), then look up the entries it points to.
Page text is in aspects["dataplex-types.global.overview"].content.
The knowledge base's rules and metric definitions are company policy: follow them, and say when a rule changes the question.""",
}


def final_sql(text: str, calls: list[dict]) -> str | None:
    """The query in the final ```sql block. No final answer means no SQL: that run counts as a failure."""
    blocks = re.findall(r"```sql\s*(.*?)```", text, re.S | re.I)
    return blocks[-1].strip() if blocks else None


async def run_one(setup: str, q: dict) -> dict:
    llm = ChatGoogleGenerativeAI(model=MODEL, vertexai=True, project=PROJECT, location="global", temperature=0)
    tools = [get_table_schema, run_sql]
    client = None
    if setup == "B":
        tools += file_tools(BUNDLE_WS / "bundle")
    elif setup == "C":
        env = {**os.environ, "PATH": f"{Path(os.environ.get('NVM_BIN', '')).as_posix()}:{os.environ['PATH']}"}
        client = MultiServerMCPClient({"kcmd": {"command": str(KCMD), "args": ["mcp", "--path", str(BUNDLE_WS)],
                                                "transport": "stdio", "env": env, "cwd": str(BUNDLE_WS)}})
        tools += [t for t in await client.get_tools() if t.name != "modify-entry"]
    agent = create_react_agent(llm, tools, prompt=BASE_PROMPT + CONTEXT_PROMPT[setup])
    stats.update(bytes=0, queries=0)
    t0 = time.time()
    error = None
    msgs = []
    try:
        out = await agent.ainvoke({"messages": [("user", q["question"])]}, {"recursion_limit": RECURSION_LIMIT})
        msgs = out["messages"]
    except Exception as e:  # noqa: BLE001
        error = f"{type(e).__name__}: {str(e)[:300]}"
    calls, tin, tout = [], 0, 0
    for m in msgs:
        for c in getattr(m, "tool_calls", None) or []:
            calls.append({"name": c["name"], "args": c["args"]})
        um = getattr(m, "usage_metadata", None) or {}
        tin += um.get("input_tokens", 0)
        tout += um.get("output_tokens", 0)
    last = msgs[-1].content if msgs else ""
    if isinstance(last, list):
        last = "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in last)
    return {"setup": setup, "id": q["id"], "question": q["question"], "answer": last, "final_sql": final_sql(last, calls),
            "tool_calls": calls, "n_tool_calls": len(calls), "input_tokens": tin, "output_tokens": tout,
            "bytes_billed": stats["bytes"], "queries": stats["queries"], "seconds": round(time.time() - t0, 1), "error": error}


if __name__ == "__main__":
    qs = {q["id"]: q for q in json.load(open(Path(__file__).with_name("questions.json")))}
    r = asyncio.run(run_one(sys.argv[1], qs[int(sys.argv[2])]))
    print(json.dumps({k: v for k, v in r.items() if k != "tool_calls"}, indent=1))
    print("tools:", [c["name"] for c in r["tool_calls"]])
