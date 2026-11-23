# Google Knowledge Catalog, Knowledge Studio and OKF: hands-on POC

**Purpose.** Find out whether Google's Knowledge Catalog stack (Knowledge Catalog, Knowledge Studio enrichment, `kcmd`, `kcagent`, OKF) can generate, review, publish and serve context about data tables to AI agents, so a team would not have to build that itself. Tested on the public dataset `bigquery-public-data.ga4_obfuscated_sample_ecommerce`.

**Status:** all steps (0–6) done, 2026-11-22/23. Start with [docs/start-here.md](docs/start-here.md), or open `report.html`. AI agents: read [AGENTS.md](AGENTS.md).

**Easiest way to read everything:** open [report.html](report.html) in a browser (download it, or clone the repo; GitHub shows HTML as source). It is one page with all results, commands and diagrams, generated from these markdown files.

## Verdict (filled in as steps complete)

| # | Capability | Verdict | Evidence |
|---|---|---|---|
| 1 | Column descriptions, sensitivity class and PII flag from my policy document | **needs a custom piece** | Policy facts land as prose pages, but there are no column descriptions or sensitivity/PII fields ([step 3](results/03-studio.md)) |
| 2 | Glossary, ontology mapping, data rules | **combine** | Data rules came through well; no glossary or ontology created ([step 3](results/03-studio.md)) |
| 3 | Per-item review, versions, approve, separate publisher, audit trail | **combine** | Per-page review; author can't self-approve; but removals aren't recorded and `kcmd push` bypasses review ([step 4](results/04-okf.md)) |
| 4 | Evidence: which source text a statement came from | **combine** | Per-page `[n]` citations; not per claim, not machine-readable ([step 3](results/03-studio.md)) |
| 5 | Serving to agents (MCP, APIs, context sets), NL-to-SQL with OKF | **use Google** (via OKF files) | Outside agent 6/15 → 10–12/15, held-out 0/3 → 3/3 ([step 5](results/05-agent.md)) |
| 6 | Procedural knowledge (playbooks, skills) | **combine** | Playbooks work as ordinary pages; no playbook type in KC ([step 4](results/04-okf.md)) |
| 7 | Nested schemas, cost and speed, Preview compliance limits | **use Google**, with Preview caveats | 29-min run, about USD 0.41 BigQuery; no task API; OKF left Google mid-POC ([step 6](results/06-verdict.md)) |

Verdict values: **use Google**, **needs a custom piece**, **combine**.

## Findings so far

- **The raw catalog holds structure, not meaning** (verified). Google creates an entry per BigQuery dataset and table within minutes, with the schema (109 nested fields for `events`), partitioning and storage. Overview, descriptions, keys, semantic types, glossary terms, labels: all empty. Same for Google's own public table. [results/01-inspect.md](results/01-inspect.md)
- **Google's sample agent `kcagent` writes one thing, a markdown overview**, grounded in the docs given and cited per file (verified). Two identical runs: same structure and sources, **0 identical sentences**. Its SQL examples: 8/8 valid for the table, **8/8 invalid for the dataset** (dataset name used as a table). [results/02-kcagent.md](results/02-kcagent.md)
- **The demo does not run as shipped in a new project** (verified): unbuilt `kcmd` dependency, errors silently dropped, hard-coded `gemini-2.5-flash` that a new project cannot call, no retry on rate limits. Fixed with small local patches. [results/02-kcagent.md](results/02-kcagent.md#2d-first-run-attempts-silent-failure-then-model-not-available-verified)
- **Studio enrichment works and is measurable** (verified). One run (29 min, ~104k tokens, ~USD 0.41 of BigQuery) turned our documents into 8 reviewed context pages; every fact from our made-up policy landed, with a citation. Studio's own eval rose **67% → 100%** (12 golden-SQL questions), and its query behaviour changed (partition filter 49% → 95%). The review is per page. Weak spots: removing a page leaves dangling index links and isn't recorded as a rejection, a confidence of 83% missed a self-contradicting page, and tasks have no API. [results/03-studio.md](results/03-studio.md)
- **Published context comes out as OKF files** (verified) with `kcmd init --kb ... --format okf --pull`. The default layout pulls nothing (403 on Google's `document` type). The kcmd MCP server serves the same text, with 3 tools. Where OKF fits: [docs/context-layer.md](docs/context-layer.md)
- **OKF, hand-written playbooks, review gates** (verified). OKF left Google on 2026-11-18 (now v0.3, vendor-neutral). `kcmd push` publishes directly (no review, not atomic); the change-request API is reviewed and **blocks self-approval** even for an Owner. [results/04-okf.md](results/04-okf.md)
- **The context helps an outside agent** (verified). A local LangGraph NL-to-SQL agent: 6/15 with no context, 10/15 reading the OKF files, 12/15 through kcmd MCP; held-out policy questions 0/3 → 3/3; about 3× less data scanned. MCP cost about 3× the tokens of the files route. [results/05-agent.md](results/05-agent.md)
- **Catalog search does not find tables in other projects** (verified): Google's public GA4 tables have entries, readable by exact name, but search returns nothing. We work on a copy in our own project. [results/01-inspect.md](results/01-inspect.md#1g-can-we-see-googles-public-tables-in-the-catalog-verified-cli)

<details>
<summary><b>Full details</b></summary>

### Layout

| Folder | Holds |
|---|---|
| [docs/](docs/) | Concepts in plain words, diagrams (SVG) |
| [poc/](poc/) | One folder per step, with the exact commands |
| [results/](results/) | One file per step: what was run, outputs, numbers, screenshots |
| [docs/screenshots/](docs/screenshots/) | Console screenshots per step (personal details removed) |
| [AGENTS.md](AGENTS.md) | Facts, IDs and file map for AI agents |
| [results/cloud-resources.md](results/cloud-resources.md) | Every cloud resource created, and how to remove it |
| [report.html](report.html) | All of the above as one readable page with diagrams. Rebuild with `uv run tools/build_report.py` (needs only `markdown==3.7`, pinned in the script) |

### Labels used for facts

- **verified**: we ran it and saw the result.
- **docs**: read in Google's documentation, not run.
- **guess**: an assumption that has not been checked yet.

### Steps

0. Setup: [poc/00-setup](poc/00-setup/), [results/00-setup.md](results/00-setup.md)
1. Inspect the catalog: [poc/01-inspect](poc/01-inspect/), [results/01-inspect.md](results/01-inspect.md)
2. Sample agent (`kcagent`): [poc/02-kcagent](poc/02-kcagent/), [results/02-kcagent.md](results/02-kcagent.md), [how it works](docs/kcagent-how-it-works.md)
3. Knowledge Studio: [poc/03-studio](poc/03-studio/), [results/03-studio.md](results/03-studio.md), [where OKF fits](docs/context-layer.md)
4. OKF and playbooks: [poc/04-okf](poc/04-okf/), [results/04-okf.md](results/04-okf.md)
5. Agent test: [poc/05-agent](poc/05-agent/), [results/05-agent.md](results/05-agent.md)
6. Verdict: [results/06-verdict.md](results/06-verdict.md)

### What I would tell a team deciding whether to build or use Google

See [results/06-verdict.md](results/06-verdict.md#what-id-tell-a-team-deciding-whether-to-build-or-use-google). In short: use Studio as the drafting and evaluation engine, keep the published context in git as OKF, give agents the files, and add your own column-level structure and one review gate.

</details>
