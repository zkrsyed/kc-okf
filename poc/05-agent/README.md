# Step 5: agent test, commands

Results: [results/05-agent.md](../../results/05-agent.md).

A local **LangGraph** ReAct agent (`create_react_agent`) on **Gemini 3.5 Flash** (Vertex AI, location `global`, temperature 0), with the same instructions in each of three setups:

| Setup | Tools | Context |
|---|---|---|
| A: no context | `get_table_schema`, `run_sql` | schema only |
| B: OKF files | A + `list_files`, `read_file` | the published context set, pulled with `kcmd init --kb ... --format okf --pull` (`results/04-okf/pull-after-push/bundle`) |
| C: kcmd MCP | A + MCP tools from `kcmd mcp` (`list-entries`, `lookup-entry`; `modify-entry` removed) | the same pulled snapshot, served over MCP (stdio) |

`run_sql` refuses queries that would bill more than 3 GB (`maximum_bytes_billed`). The step limit is 60 graph steps (about 30 tool calls). A run counts only if the agent ends with one final SQL code block.

Pinned versions (`pyproject.toml`, `uv.lock`): langgraph 1.2.24, langchain-google-genai 4.5.2, langchain-mcp-adapters 0.3.2, google-cloud-bigquery 3.47.0, Python 3.12.

```bash
cd ~/apps/kc-okf/poc/05-agent
export CLOUDSDK_ACTIVE_CONFIG_NAME=kc-okf     # ADC must have the POC project as quota project
nvm use default                               # Node for kcmd (setup C)
uv sync
uv run python -W ignore agent.py B 15         # one question in one setup, prints the run
```

```bash
# all 15 questions, one process per setup (they run in parallel; Vertex 429s are retried with back-off)
for s in A B C; do nohup uv run python -W ignore run_all.py $s > ../../results/05-agent/progress-$s.log 2>&1 & done
```

```bash
# run every final SQL and every golden SQL in BigQuery and compare -> scores.csv, summary.md
uv run python -W ignore score.py
```

The questions, golden SQL, alternates (other equally valid readings) and policy checks are in [questions.json](questions.json). Questions 1 to 12 are Studio's eval set; **13 to 15 are held out**: Studio never saw them.
