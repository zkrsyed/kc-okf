# For AI agents: what this repo is and the facts it holds

You're reading the record of a proof of concept (POC) run on 2026-11-22/23. It evaluated **Google Knowledge Catalog** (Dataplex), **Knowledge Studio** enrichment (Preview), **kcmd** 0.2.5, **kcagent** (Google's sample agent) and **OKF** (Open Knowledge Format) as a *context layer* for data agents. The main use case is natural-language-to-SQL over BigQuery. Use this file to answer questions about the POC or to compare Google's approach with a home-grown context agent. Every claim in the results files is labelled **verified** (run and observed), **docs** (from documentation or a spec) or **guess** (not checked). Keep those labels when you repeat a claim.

## Where things are

| Path | What |
|---|---|
| `report.html` | Everything below rendered as one page, with screenshots and diagrams (built by `uv run tools/build_report.py`) |
| `docs/start-here.md` | Two-minute summary and reading guide |
| `results/0N-*.md` | What happened in step N, with evidence; `results/0N-*/` holds raw outputs |
| `poc/0N-*/README.md` | Exact commands for step N |
| `docs/context-layer.md` | Where KC, Studio, kcmd and OKF sit in an agent's context layer; how outside agents read it; playbooks |
| `results/06-verdict.md` | Verdict per capability, and a comparison checklist for custom agents |
| `results/cloud-resources.md` | Every cloud resource created and how to remove it |
| `docs/screenshots/<step>/` | Console screenshots (personal details removed) |
| `vendor/` | Git-ignored third-party checkouts (pinned commits are recorded in results) |

## Environment (public sample only; no work data)

- GCP project `kc-okf-poc-261122` (number 109873812728), catalog location `us`, Studio task region `us-central1`.
- Data: `kc-okf-poc-261122.ga4_sample.events`. One table built from Google's public `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`: 4,295,584 rows, 2020-11-01 to 2021-01-31 (92 days), partitioned on `event_date_dt`, heavily nested (109 field paths).
- **Tracer facts** come from a made-up policy document (`poc/03-studio/signals/merch-store-data-policy.md`) that exists nowhere else: dataset code MSC-417, owner "Digital Insights Guild", channel `#msc-417-data`, data final 72 hours after the day ends, tiers C1/C2/C3 (`user_pseudo_id` C2, never export or join with CRM; `geo.city`/`geo.metro` C3, region/country only), 14-month retention, engaged session (>10 s, or 2+ page views, or a purchase), active buyer 28d, net merch revenue = purchase revenue in USD minus refunds in USD, exclude `traffic_source.source = '(data deleted)'` from attribution.

## Key results (all verified unless marked)

**Raw catalog (step 1).** Google auto-creates entries with the schema, but overview, column descriptions, keys, semantic types and glossary terms are all empty. Catalog search doesn't find tables in other projects.

**kcagent (step 2).**

- It needed 2 patches to run in a new project (errors were silently dropped; the hard-coded `gemini-2.5-flash` returned 404).
- It has no retry on 429.
- It writes one Markdown overview per entry. Two identical runs shared 0 sentences.
- Its SQL examples were valid 8/8 for the table but invalid 8/8 for the dataset.

**Studio run 1 (step 3).**

- Inputs: Google's 8 sample docs plus the policy doc (GCS signal), and a 12-question golden-SQL eval set.
- It ran 29 min 12 s, used 104,025 tokens (free in Preview), and ran 209 BigQuery jobs (65.2 GB, about USD 0.41).
- Studio's own eval: baseline 67% (8/12), projected 100% (12/12).
- The agent's SQL before and after its own context: partition filter 49% → 95%; scans over 1 GB 30 → 1; `(data deleted)` excluded 0 → 15.
- It proposed 9 creates in one change request: a root page, 3 index pages, a table page, 3 topic pages and 1 entry link.
- Every tracer fact appeared, cited as `[n]` to the policy doc. Confidence: 83–87% "High".
- One page (`pitfalls`) contradicted itself, yet scored 83%.

**Review (steps 3–4).**

- Per-page approve or remove. Removed pages are erased, not counted as "rejected", and the index pages still link to them.
- Approval needs `dataplex.changeRequests.use` (roles `workflowApprover`, `workflowAdmin`, `catalogAdmin`, `dataplex.admin`, basic Editor/Owner). `dataplex.editor` can run tasks but not approve.
- **Authors cannot approve their own change request**: `403 "User is not authorized to approve their own ChangeRequest"`, even as Owner.
- The `approverEmails` field on a context set only notifies; it doesn't restrict who approves (**docs**).
- Change requests have a REST API (`get/list/approve/reject/delete`, `entryGroups:requestBatchMetadataChange`). Studio tasks have none (`agentTasks` has IAM methods only).

**Where Studio's output lives.** Only as `document` entries inside the context set (entry group type `context-set`). The real BigQuery table entry still has 0 of 24 column descriptions; Studio wrote no column descriptions, sensitivity aspects or glossary terms.

**Reading context out (step 3).**

- `kcmd init --kb <project>.<location>.<context-set> --pull` (default layout) pulls nothing: `GET entryTypes/document` returns 403, and kcmd 0.2.5 treats that as fatal for the type.
- `--format okf` works: 7–8 Markdown files with YAML frontmatter (`type` plus an `x-kcmd` block) and `_links.yaml`.
- `kcmd mcp` serves `list-entries` (names only), `lookup-entry` (JSON with the page in `aspects["dataplex-types.global.overview"].content`) and `modify-entry` (a write). There's no tool for entry links, and the README's `pull`/`push` MCP tools and `kcmd status` don't exist in 0.2.5.
- Studio names the root page `agents.md`; kcmd treats `agents.md` and `index.md` as interchangeable roots.

**OKF (step 4).**

- `GoogleCloudPlatform/open-knowledge-format` was deprecated on 2026-11-18. OKF moved to `open-knowledge-format/open-knowledge-format` (spec v0.3, with agent skills `okf-consume` and `okf-generate`).
- KC's export is only loosely OKF. It parses, but has no `title`, `description`, `generated`, `verified`, `sources` or `index.md`, and it cites with `[n]` lists instead of footnotes. So an OKF consumer treats every page as "unverified", even after human approval in Studio.
- OKF has a first-class `type: Playbook` (**docs**).

**Writing context by hand (step 4).**

- `kcmd push` writes directly (`batchChangeMetadata`), with **no change request**.
- Pushes are **not atomic**: the first push applied 2 of 3 changes and rejected a page that lacked the `dataplex-types.global.document` aspect.
- The reviewed route is `requestBatchMetadataChange`. It creates a change request in state NEW, and nothing is published until a *different* person approves.

**Agent test (step 5).** Strict pass rates: **A 6/15, B 10/15, C 12/15**. Reviewed for defensible readings: 6, 13, 14. Held-out questions 13–15: **A 0/3, B 3/3, C 3/3**.
- The city rule was broken twice by A and never by B or C.
- The partition filter was used in 9 / 14 / 15 of 15 runs, and GB scanned was 44.9 / 16.6 / 14.9.
- MCP used about 3× the tokens of the files route for the same accuracy.
- Both context setups opened `agents` first in 15 of 15 runs, and read the hand-written playbook in 12–14 runs.
- Details are in `results/05-agent.md`.

The setup:

- a local LangGraph ReAct agent on Gemini 3.5 Flash (Vertex)
- 15 questions: Studio's 12, plus 3 held out
- three setups: A, schema only; B, the published context as OKF files; C, the same pages via `kcmd mcp`
- scoring: the final SQL result is compared with golden SQL in BigQuery

## How to compare this with a custom context agent

Use `results/06-verdict.md` → "Comparing with a home-grown context agent". It lists the dimensions (input sources, grounding and citations, review gate, separation of duties, freshness, serving path, playbooks, evaluation, cost and latency, lock-in) and what Google's stack did on each in this POC. Run the same 15 questions (`poc/05-agent/questions.json`, golden SQL included) against the custom agent's context with `poc/05-agent/score.py` to get comparable numbers.

## Caveats

- One Studio run, one table, one dataset (public, obfuscated). Studio is in Preview and changes week to week.
- Step 5 ran each question once per setup, to keep cost low. Gemini at temperature 0 still varies between runs, so treat a difference of one or two questions as noise.
- Questions 1–12 were Studio's own eval set, so its context was tuned on them; questions 13–15 are the fair held-out check.
