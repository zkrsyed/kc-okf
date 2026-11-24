# Step 6: verdict, capability by capability

**The question:** can Google's Knowledge Catalog stack (Catalog, Knowledge Studio, kcmd, OKF) generate, review, publish and serve the context that data agents need, so a team doesn't have to build that layer itself?

**Verdict values:** **use Google** = it does the job as is; **combine** = use Google's piece plus a thin piece of our own; **needs a custom piece** = Google doesn't cover it today. All of this is based on one Preview run, one table, 2026-11-22/23.

## The verdict table

| # | Capability | Verdict | Why (evidence) |
|---|---|---|---|
| 1 | Column descriptions, sensitivity class and PII flag from my policy document | **needs a custom piece** | Studio put every policy fact into *prose pages* (tiers C1/C2/C3, `user_pseudo_id` C2, `geo.city` C3), correctly and with citations. But it wrote **no column descriptions, no sensitivity aspect and no PII flag**: the BigQuery table entry still has 0 of 24 column descriptions. To get structured, column-level classification (for policy tags or masking), write it yourself (kcmd push of aspects, or the API). [Step 3](03-studio.md) |
| 2 | Glossary, ontology mapping, data rules | **combine** | The **data rules** came through well as prose (finality, attribution exclusion, geo aggregation, net revenue). **No glossary terms or ontology** were created. Studio can *read* glossaries as signals, and the context set has an "Ontology included in enrichment" field, but we didn't test it. A business glossary has to be authored separately. [Step 3](03-studio.md) |
| 3 | Per-item review, versions, approve, separate publisher, audit trail | **combine** | Strong: a **per-page** review (view, edit, remove, approve), and **an author can never approve their own change** (403 even for Owner). The change request records author, approver and comments, and change requests are scriptable. Weak: removals are erased (no "rejected" record), the index pages keep links to removed pages, **`kcmd push` bypasses review**, pushes aren't atomic, and we saw no version history of a page. Add a git-based review for hand-written context and a check that fails a change set with dangling links. [Steps 3–4](04-okf.md) |
| 4 | Evidence: which source text a statement came from | **combine** | Every page cites its sources as `[n]` with a reference list naming the document, and every tracer fact traced back to the policy doc. But citations are **per page, not per claim, and not machine-readable**: no OKF `sources`/footnotes and no link to the exact passage. The confidence score (83–87%) didn't catch a self-contradicting page. Treat Studio's citations as reviewer aids, not as provenance. [Steps 3–4](03-studio.md) |
| 5 | Serving to agents (MCP, APIs, context sets), NL-to-SQL with OKF | **use Google** (via OKF files) | Published context comes out as OKF Markdown with `kcmd --format okf` (the default layout fails), through kcmd's local MCP server, and through the REST API. Any agent, inside or outside Google, can read it. Measured in step 5: a local LangGraph agent went from **6/15 to 10–12/15** (strict) and from **0/3 to 3/3 on held-out policy questions** with this context. OKF files and MCP scored the same within noise, but MCP used about 3× the tokens. [Steps 3, 5](05-agent.md) |
| 6 | Procedural knowledge (playbooks, skills) | **combine** | Studio drafts how-to pages itself (a "computing metrics" page with SQL). Hand-written playbooks work as ordinary `document` pages, through kcmd push (direct) or a change request (reviewed). There's no playbook type or behaviour in KC; OKF has `type: Playbook`. Author playbooks in git as OKF and push them; let Studio draft, but don't trust it with exact SQL. [Step 4](04-okf.md) |
| 7 | Nested schemas, cost and speed, Preview limits | **use Google**, with Preview caveats | Nested GA4 schema handled well (UNNEST patterns, session key). One run: 29 min, about 104k tokens (free in Preview), about USD 0.41 of BigQuery, plus about 5 min to create a task (the console doesn't say it's still creating). Preview limits: tasks are console-only (no API), Google's `document` type definition is unreadable (403), OKF moved out of Google mid-POC, and the run's query-history read failed with a 403 we couldn't explain. [Steps 3–4](03-studio.md) |
| 8 | Does a custom instruction close the column-coverage gap? (Studio run 2, step 7) | **no: needs a custom piece** | Asked explicitly for a description, tier and personal-data flag per field, glossary terms and one item per rule. Studio wrote more prose (24 of 24 columns instead of 12, tiers inline, a 5-term glossary section, 8 numbered rules; 4 right, 4 vague, 0 wrong on a 30-field sample) but still **0 column description fields, 0 glossary terms, 0 rule objects**, and one wrong tier statement at 84% confidence. The pages still helped an outside agent: 12/15 strict with files and with MCP, 3/3 held-out. Ontology couldn't be tested: nothing sets it. [Step 7](07-studio-run2.md) |

## What I'd tell a team deciding whether to build or use Google

1. **Use Studio as the drafting engine, not the source of truth.** It's genuinely good at turning scattered documents into agent-ready pages and proving, with your own eval set, that the pages change query behaviour. It found and used every fact we planted. Building that yourself means building document ingestion, grounding, an evaluation loop and a review UI.
2. **Keep the source of truth in git as OKF.** Pull what Studio publishes (`kcmd init --kb ... --format okf --pull`), commit it, and let your agents read those files. You get diffs, blame, rollback and portability. Hand-written playbooks live in the same tree.
3. **Put one review gate in front of publishing, and make it the only one.** Either git pull requests plus `kcmd push` (fast, but the catalog won't enforce anything), or change requests through the API (the catalog enforces a two-person rule). Don't mix them without a rule: `kcmd push` silently skips the catalog's review.
4. **Add the missing structure yourself where it matters for control.** Column-level sensitivity and PII flags, policy tags and a glossary aren't produced. If masking or access control depends on them, generate them in your own pipeline (for example an LLM pass over Studio's prose; not tested here) and write them as aspects.
5. **Measure with your own questions.** Studio's eval set is the best part of the product. Keep a held-out set it never sees, because its 100% on the questions it tuned for isn't the same as general accuracy. In step 5 the context passed all 3 held-out questions, but one setup still used GA4's own "engaged session" flag instead of the policy's definition, which only a golden-SQL check catches.

## Comparing with a home-grown context agent

Your own agents (retriever over GCS docs plus embeddings, or an OKF-reading agent) do the same job. Compare on these dimensions; the right-hand column is what Google's stack did in this POC.

| Dimension | Question to ask of the custom agent | Google stack in this POC |
|---|---|---|
| Inputs | Which sources can it read? | GCS files, glossaries, BigQuery query history; connectors for Drive/Docs/Sheets/Slides, Confluence, Jira, GitHub, SharePoint (console list, not tested) |
| Grounding | Can every statement be traced to a source? | Per-page `[n]` citations; every planted fact traced; not per claim |
| Output shape | Prose, structured fields, or both? | Prose pages (root, indexes, table page, topic pages); no column fields |
| Evaluation | Does it test its own output against golden questions? | Yes: baseline vs projected on your eval set, plus SQL-behaviour change visible in logs |
| Review | Who approves, per item or all at once, and is it recorded? | Per page; two-person rule enforced for change requests; removals not recorded |
| Bypass | Can someone publish without review? | Yes, `kcmd push` with `contentEditor` |
| Serving | How does an agent read it? | OKF files, kcmd MCP (local), REST API; agents anywhere |
| Process knowledge | Where do playbooks live? | `document` pages; hand-written via push or change request |
| Freshness | How does it stay current? | Rerun the task (on demand or scheduled); pull again; self-learning option not tested |
| Cost and speed | Per run? | About 30 min; Preview tokens free; BigQuery bytes billed to you |
| Lock-in | Can you leave? | Yes: OKF export is plain Markdown (needs a light conversion for full OKF v0.3) |

**To get comparable numbers**, run the custom agent's context through the same harness: [`poc/05-agent/questions.json`](../poc/05-agent/questions.json) (15 questions with golden SQL, alternates and policy checks) and [`poc/05-agent/score.py`](../poc/05-agent/score.py). Add a setup to `agent.py` that gives the agent your context, then compare pass rates, especially on the held-out questions 13–15.
