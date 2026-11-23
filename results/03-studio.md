# Step 3: Knowledge Studio (context set, enrichment task, review)

Status: in progress (2026-11-22).

## Setup done

| Item | Value |
|---|---|
| Execution service account | `kc-studio-enricher@kc-okf-poc-261122.iam.gserviceaccount.com` with the 7 project roles from Google's docs |
| Dataplex service agent | `service-109873812728@gcp-sa-dataplex.iam.gserviceaccount.com`: `serviceAccountTokenCreator` on the execution account, `bigquery.dataViewer` on the project |
| Signals bucket | `gs://kc-okf-poc-261122-signals` (US): Google's 8 sample docs under `google-sample/` and our made-up [policy doc](../poc/03-studio/signals/merch-store-data-policy.md) |
| Eval set | [poc/03-studio/eval-set.jsonl](../poc/03-studio/eval-set.jsonl) in its own bucket `gs://kc-okf-poc-261122-eval`: 12 questions with golden SQL; 5 need only the schema, 7 need the made-up policy doc to get right (see below) |
| Context set | `ga4-merch-context`, location `us` (multi-region), created in the console |

## Tracer facts

The made-up policy doc contains facts found nowhere else: dataset code `MSC-417`, business name "Merch Store Clickstream", team "Digital Insights Guild", tiers "C2"/"C3", the 72-hour rule, the "Net merch revenue" formula. If they show up in Studio's output, Studio read our doc. **verified** that they are absent from Google's docs and from step 2's kcagent output (they were written after it).

## Findings so far

- **Console location list:** the context-set form defaults to `us-central1`; multi-regions (`us`, `eu`, `global`, ...) are at the top of the list under "Multi-region". Location cannot be changed later. **verified**
- **Project Owner cannot read a context set.** Right after creating it, the details page showed `Permission 'dataplex.entries.listContext' denied` for the Owner. **verified** The context permissions are only in the Dataplex *content* roles, not in Owner/Editor or the Catalog roles (read with `gcloud iam roles describe`, **verified**):

| Role | Context permissions |
|---|---|
| `dataplex.editor`, `dataplex.admin` | `entryGroups.createContextSet` only |
| `dataplex.contentViewer` | `getContextSet` |
| `dataplex.contentUser` | get/list context, `requestContextChanges` |
| `dataplex.contentEditor` | create/update/delete/get/list context, `requestContextChanges`, `updateContextSet` |
| `dataplex.contentAdmin` | contentEditor plus `deleteContextSet` |
| `dataplex.workflowApprover` (Beta) | `changeRequests.get/list/use` (approving changes) |
| `dataplex.catalogEditor`, `catalogAdmin` | `useContextAspect/Entry/EntryLink` only |

So a team needs to hand out these roles on purpose: creating a context set and reading it are separate permissions.

- **After granting `roles/dataplex.contentEditor` to my user**, the context set page loads without the error, *Edit* becomes clickable, and *Delete* stays greyed out (matches the table: only `contentAdmin` has `deleteContextSet`). **verified**
- The context set page has fields **Enrichment task** and **Ontology included in enrichment** (both empty), and an **Entries** list with columns Name, Description, Entry type, Linked assets, Last modified. So a context set holds its own entries that *link to* assets such as tables. **verified** (what the screen shows) / **guess** (what "Linked assets" will contain).
- **The enrichment task is a 4-page wizard:** 1 Define (display name, task ID that cannot be changed later, custom instructions "in one or two sentences"), 2 Scope ("what gets enriched, and what the agent reads"), 3 Improve ("evaluation and self-learning"), 4 Run ("trigger and notifications"). **verified**
- **Scope page** (verified, from the console):
    - *Context set* (required): "the context set this task enriches and saves its results to". Can create one inline.
    - *Enrichment task region* (required): "required for context sets in a multi-region"; defaults to `us-central1`.
    - *Resources to enrich*: "Default resources: everything in the context set is enriched by default", plus optional *Add more resources* (BigQuery datasets/tables, or Lakehouse catalogs/namespaces/tables).
    - With an empty context set and no resources the page warns: "Running this task will create a knowledge base and will not enrich any entries."
    - *Knowledge signals*: "extra sources the agent reads for context. These are not enriched": Cloud Storage buckets, folders (path ending in `/`) or files; Glossaries.
- Task ID used: `ga4-events-enrichment`.
- Scope as filled: resource `kc-okf-poc-261122.ga4_sample.events` (table only); signal bucket `kc-okf-poc-261122-signals` (whole bucket); no glossaries. Console note: "Adding new resources to this task will add them to the context set." A collapsed **External sources** section sits below Glossaries. **verified**
- **Improve page** (verified, from the console):
    - *Evaluation set*: "a .jsonl file in Cloud Storage. Measures the impact of proposed context changes."
    - *Curation set*: "a .jsonl file in Cloud Storage. Set of questions to hillclimb on." So Studio separates a training-style set (curation) from a held-out test set (evaluation).
    - *Publishing*: "Enable auto-publish: automatically publish changes that meet the quality threshold" (off by default). Human review is the default.
    - *Self-learning*: "finds gaps in real agent conversations and keeps your context current" (toggle, off by default).
- Choice for run 1: evaluation set only, no curation set, auto-publish off, self-learning off. Reason: a clean baseline where every change goes through human review and the 15 questions are never used to tune the context.
- The eval file goes in a **separate bucket** (`gs://kc-okf-poc-261122-eval`), because the whole signals bucket is a knowledge signal: an eval file there would let the agent read the answers.
- **External sources** (Scope page, collapsed by default; verified from the console): "Includes Google Workspace, Microsoft SharePoint, GitHub, and Atlassian Confluence." Connected sources, each with a *Set up* button: **Google Workspace** (Drive, Docs, Sheets, Slides), **Atlassian** (Confluence spaces and Jira projects), **GitHub** (repositories and READMEs), **Microsoft** (SharePoint sites). Optional *Source configuration file*: a Cloud Storage YAML file to configure third-party connections. Not used in run 1. This is wider than the docs we read in step 0, which named only Cloud Storage and Workspace (**docs** vs **verified**).
- **Eval set format:** my first file put `golden_response` next to `evaluation_request` (my reading of the docs). The console rejected it: `Line 1: missing "evaluation_request.golden_response.text"`. Correct shape, **verified** by the console's validator: `{"evaluation_request": {"prompt": {"text": "..."}, "golden_response": {"text": "..."}}}`. The console checks the file as soon as you pick it, which is helpful.
- **The evaluation set is about SQL.** After loading the file, the preview table's columns are *Name, Prompt, **Golden SQL***. **verified** So Studio measures whether an agent writes the right query with the context, not whether it answers in prose. Our first set had prose answers (kept as `trash/eval-set-prose-v1.jsonl`); it was rewritten as 12 questions with golden SQL in [poc/03-studio/eval-sql/](../poc/03-studio/eval-sql/). All 12 pass a BigQuery dry run (**verified**, [dry-run.txt](../poc/03-studio/eval-sql/dry-run.txt)).

## Eval set (golden SQL)

| # | Question | Needs the policy doc? | What the right SQL must do |
|---|---|---|---|
| 1 | Total sessions | no | count distinct `user_pseudo_id` + `ga_session_id` on `session_start` |
| 2 | Daily active users, Dec 2020 | no | filter on partition column `event_date_dt` |
| 3 | Top 10 products added to cart | no | unnest `items` |
| 4 | Top pages on 2021-01-15 | no | pull `page_location` out of `event_params` |
| 5 | Purchases per day, first week of Jan 2021 | no | partition filter |
| 6 | Net merch revenue, Dec 2020 | **yes** | `purchase_revenue_in_usd` minus `refund_value_in_usd` |
| 7 | Active buyers (28d) as of 2021-01-31 | **yes** | trailing 28 days of `purchase` |
| 8 | Users **by city**, Jan 2021 | **yes** | group by country/region instead (city is Tier C3) |
| 9 | Sessions by traffic source for attribution | **yes** | exclude `(data deleted)` |
| 10 | Cart conversion rate, Dec 2020 | **yes** | sessions with purchase / sessions with add_to_cart |
| 11 | Engaged sessions, Jan 2021 | **yes** | >10 s, or 2+ page views, or a purchase |
| 12 | Daily net merch revenue, Jan 2021, **final days only** | **yes** | drop the last 3 days (72-hour rule) |

Facts with no SQL form (owner team, dataset code `MSC-417`, "never join with CRM") are tested in step 5 instead.

## Screenshots

![Create context set form: display name, ID, description, location (default us-central1)](../docs/screenshots/03-studio/01-create-context-set-form.webp)

![Location list: single regions](../docs/screenshots/03-studio/02-location-regions.png)

![Location list: multi-regions at the top, including us](../docs/screenshots/03-studio/03-location-multiregion.png)

![Context set created in us; project Owner gets "Permission dataplex.entries.listContext denied"](../docs/screenshots/03-studio/04-owner-listcontext-denied.webp)

![After granting Dataplex Content Editor: no error, Edit enabled, Delete still greyed out](../docs/screenshots/03-studio/05-context-set-after-contenteditor.webp)

![Enrichment task wizard, page 1 Define: display name, task ID, custom instructions](../docs/screenshots/03-studio/06-task-define.webp)

![Page 2 Scope: choosing the context set](../docs/screenshots/03-studio/07-task-scope-pick-context-set.webp)

![Scope: warning for an empty context set, task region us-central1](../docs/screenshots/03-studio/08-task-scope-empty-warning.webp)

![Scope filled: events table as resource, signals bucket, note that resources are added to the context set](../docs/screenshots/03-studio/09-task-scope-filled.webp)

![Page 3 Improve: evaluation set, curation set, auto-publish, self-learning](../docs/screenshots/03-studio/10-task-improve.webp)

![External sources: Google Workspace, Atlassian, GitHub, Microsoft SharePoint](../docs/screenshots/03-studio/11-task-external-sources.webp)

![Evaluation set: "Object not found" before the eval bucket existed](../docs/screenshots/03-studio/12-eval-object-not-found.webp)

![Evaluation set validator: missing evaluation_request.golden_response.text](../docs/screenshots/03-studio/13-eval-format-error.webp)

![Evaluation set preview: columns Name, Prompt, Golden SQL](../docs/screenshots/03-studio/14-eval-preview-golden-sql.webp)

![Evaluation set accepted: 12 items with golden SQL; curation set left empty, auto-publish and self-learning off](../docs/screenshots/03-studio/15-eval-preview-12-sql-items.webp)

- **Run page** (verified, from the console): *Run as* "the identity this task uses to read the configured sources and write to the context set": a required **user service account** picker listing the project's service accounts (ours, plus the Compute Engine default account that appeared when the Compute API was turned on), with a *New service account* button. *Trigger*: default **On demand**, with a schedule option. *Notifications*: "email a report after every run", up to five addresses. The final button is **Create**.

![Run page: Run as service account picker, trigger, notifications](../docs/screenshots/03-studio/16-task-run-as-service-account.webp)

- **After Create** (verified): the Enrichments list shows counters *Active 0 / Failed 0 / Succeeded 0* and one row `ga4-events-enrichment` with an empty Status and Run summary and **Trigger "Scheduled"**, although the Run page summary said "On demand". So Create made the task but did not visibly start a run.

![Enrichments list right after Create: task listed, no status, trigger "Scheduled"](../docs/screenshots/03-studio/17-enrichments-list-after-create.webp)

- **Task page** (verified): buttons *Edit, Delete, Refresh, **Run now***; tabs *Jobs* and *Details*. The Jobs tab (columns Name, Status, Last Update Time, Duration, **Tokens Used**, Summary, Actions) showed "Sorry, the server was not able to fulfill your request" before any run existed. **guess**: the Preview UI errors on an empty job list rather than a permission problem.
- **Not scriptable yet.** The task is not a Dataplex DataScan (`gcloud dataplex datascans list` is empty). The public Dataplex v1 discovery document has a resource `projects.locations.agentTasks`, but it exposes only `getIamPolicy`, `setIamPolicy` and `testIamPermissions`; GET on `.../agentTasks` returns "Method not found". **verified** (2026-11-22). So enrichment tasks can only be driven from the console for now: no gcloud, no public REST, no Terraform.

![Task page before the first run: Run now button, Jobs tab with a server error](../docs/screenshots/03-studio/18-task-page-jobs-error.webp)

- **Create is slow and silent.** Audit logs (**verified**, `gcloud logging read`) show `AgentTaskService.CreateAgentTask` at 22:02:37 (UTC) as a long-running operation that finished at 22:07:04: **about 4.5 minutes** to create the task. The console listed the task (trigger "Scheduled", no status) during that time with no "creating" indicator. Clicking *Run now* at 22:06:26 failed with `INVALID_ARGUMENT: Provided AgentTask '.../locations/us-central1/agentTasks/ga4-events-enrichment' does not exist.` The operation result is saved in [03-studio/create-agenttask-operation.json](03-studio/create-agenttask-operation.json): resource type `google.cloud.dataplex.v1.AgentTask`, location `us-central1`.
- **What is visible from outside the console:** the API service is `google.cloud.dataplex.v1.AgentTaskService` (methods seen: `CreateAgentTask`, `RunAgentTask`); calls appear in Cloud Audit Logs, and the create operation can be read with the standard operations API. The REST methods themselves are not in the public discovery doc. **verified**

![Run now clicked before creation finished: "AgentTask ... does not exist"](../docs/screenshots/03-studio/19-run-now-agenttask-does-not-exist.webp)

- **Task Details tab** (verified) lists everything in one place: context set `projects/kc-okf-poc-261122/locations/us/entryGroups/ga4-merch-context` (so a context set **is** an entry group, as the docs said), region `us-central1`, resources "Tables: kc-okf-poc-261122.ga4_sample.events", assets (buckets) `kc-okf-poc-261122-signals`, the service account, the evaluation set, *Auto-publish quality threshold* and **Regression threshold** (both empty: two settings the wizard did not show), trigger **On demand**. So the "Scheduled" label in the task list is wrong or means something else.
- **Run 1 started** at 22:07 UTC on 2026-11-22, run ID `d3704062-699a-4661-9299-1d42e5d4266d`. The run page has tabs *Overview* (Enrichment Report: status, duration, tokens, summary) and *Logs*. First status: **Pending**.

![Task Details tab: full configuration, trigger On demand](../docs/screenshots/03-studio/20-task-details.webp)

![Run 1 started: status Pending](../docs/screenshots/03-studio/21-run-started-pending.webp)

- **The agent queries the data.** Audit logs for `kc-studio-enricher` during run 1 (**verified**, snapshot at about 12 minutes in): 138 completed BigQuery jobs, 0 errors, **52.5 GB billed** (about USD 0.33 at on-demand prices; inside the 1 TB/month free tier). The first queries list schemas, tables, columns and routines through `INFORMATION_SCHEMA`, then profile the data (min/max date, row counts) and run analytical queries that look like attempts at our eval questions. Several queries do not filter on the partition column and scan 1.35 GB each. The Dataplex service agent only called `GenerateAccessToken` (the badge swap). Every job of the full run and its SQL: [03-studio/run1-bq-jobs.csv](03-studio/run1-bq-jobs.csv).
- **Cost note for a team:** enrichment is free during Preview, but the BigQuery queries it runs are billed to the project like any other query. On large tables, a team should cap this with a per-user or per-project query quota or custom cost controls for the service account.

![Run 1 after 12 minutes: Running](../docs/screenshots/03-studio/22-run-running-12min.webp)

## Run 1: what happened behind the scenes

The console's *Logs* tab reads Cloud Logging, log `dataplex.googleapis.com/agent_task`, entries of type `google.cloud.dataplex.v1.AgentTaskEvent` (event types `EXECUTION_LOG` and `AGENT_RUN_EVENT`). [tools/export_run_log.py](../tools/export_run_log.py) exports a run's entries to [03-studio/run1-agent-log.md](03-studio/run1-agent-log.md) (readable) and `.jsonl` (raw). Findings from the log, all **verified** unless marked:

- **A 7-stage pipeline**: `prepare` (5%), `baseline_eval` (15%), `source_gather` (20%), `entry_writing` (45%), then later stages. Queued for about 8 minutes before the first stage (run started 22:08:27, stage 1 at 22:16:47 UTC).
- **Baseline first.** Stage 2 `baseline_eval` took about 6.5 minutes. The BigQuery jobs in that window look like answers to our eval questions written *without* the new context, so Studio measures a "before" score. **guess** (from timing and the SQL in the jobs snapshot).
- **Model:** `gemini-3.8-flash`.
- **Our documents were read.** "9 gathered" items from Cloud Storage (our 8 Google files and the policy doc); all were under the 8,000-character "size gate", so they were used whole without a summarising model call. The `[Crawler]` "fetched 0 documents" line refers to the external connectors, which we did not set up.
- **Tracer, first sign:** the `[Router]` step matched the table to our made-up doc: `events ← Merch Store Clickstream: data policy and metric definitions, table metadata, data sample (used only to check accuracy)`. The business name exists only in our policy doc.
- **Mention extraction:** "Source documents mention 4 tables, 20 columns, 9 glossary terms and 10 other systems (51 times in total)". So Studio extracts glossary-like terms from documents even with no glossary configured.
- **Query history.** Studio tries to learn from 30 days of real query history for the table ("sample queries"), but failed with `403 ... customer permission check failed for bigquery.jobs.listAll`. Our service account **does** have `roles/bigquery.resourceViewer`, which includes `bigquery.jobs.listAll` (checked with `gcloud iam roles describe`). Why it still failed is unknown (**guess**: the check runs as a different identity or at another level). Google's setup docs do not mention this permission. It would matter on a real table with real usage; here there was no history anyway.
- **Relationships:** a `[Link]` step looks for related tables from document co-mentions and schema overlap ("1 verifier candidate pair ... from schema overlap"), and added 0 links. That is the console's *Relationships* feature.
- **Output so far:** "wrote 2 file(s)" for `miscellaneous/events`, created 1 context-set asset entry for `events` linked to its source table, and planned **3 context entries** in category `analytics-guidelines`.

![Run 1 Logs tab in the console](../docs/screenshots/03-studio/23-run-logs-tab.webp)

### Run 1 result

- **Succeeded.** Run started 22:08:27, completed 22:37:39 UTC: **29 minutes** (about 8 of them queued). **verified**
- **Run summary** (from the final `AGENT_RUN_EVENT`): "High confidence overall: 4 proposals scored across 9 changes -- 4 High, 0 Medium, 0 Low." **Tokens:** 83,969 in, 20,056 out, 104,025 total. One **change request** created: `projects/109873812728/locations/us/changeRequests/345f4080-d80d-4ae6-85ce-a856cda1ae23`, "staged (auto-publish is off; staged for review)". **verified**
- **Later stages:** wrote 3 documents `pitfalls`, `data-governance-and-quality-boundaries`, `computing-standard-ecommerce-metrics`; organised them into folders; rewrote the context set's description; skipped a "semantic model step" on a temporary copy `ga4-merch-context-curate-tmp-...`; `finalize_catalog` (88%, "models and redaction"); `final_eval` (92%, about 5.5 minutes); `publish` (95%, "staging change requests and run reports"). **verified**
- **BigQuery work by the service account over the whole run:** 209 jobs, 0 errors, **65.2 GB billed (about USD 0.41 on-demand, inside the free tier)**. [03-studio/run1-bq-jobs.csv](03-studio/run1-bq-jobs.csv). **verified**

- **Console Jobs tab after the run:** status **"Needs review"** (a warning icon, not "Succeeded"), duration 29 min 12 sec, Tokens Used 104K, and the same summary text. The log says SUCCEEDED; the console shows the human-facing state: the run is done but its change request is waiting for a reviewer. **verified**

![Screenshot 24: Jobs tab after run 1, status Needs review, 29 min 12 sec, 104K tokens](../docs/screenshots/03-studio/24-jobs-needs-review.webp)

#### Studio's own scores (run Overview tab)

From the user's screenshot of **Enrichments > ga4-events-enrichment > run d3704062 > Overview** (the image file was not saved in the session, so it isn't embedded here): **verified**

| Field | Value |
|---|---|
| Enrichment Report score | **83%, High** |
| End-to-end evaluation, Baseline | **67%** (8 of 12 pass) |
| End-to-end evaluation, Projected | **100%** (12 of 12 pass) |
| Delta | **+4 (+33%)**, "Cases with a baseline: 12" |
| Proposals | author `kc-studio-enricher@...`, "Enrichment Agent Proposal: Knowledge Base Entry", buttons **Deny** / **Approve (9)** |

"Projected" means Studio's final eval ran against the *proposed* context before anyone approved it. It isn't a measurement of the published context. The page also has **Evaluation** and **Artifacts** tabs, which we haven't opened yet.

#### The proposals (the change request)

![Screenshot 25: run page Proposals list, 9 creates grouped as Document entries, Index entries and Entry links, each with its own checkbox and View proposal](../docs/screenshots/03-studio/25-run-review-proposals.webp)

- **9 changes, all Create** (0 Update, 0 Delete). The filter chips say High 4, N/A 5: the 4 content pages get a confidence score; the index pages and the link don't. **verified**
- **Review is per item, not all-or-nothing.** Each proposal has a checkbox, with **Remove selected** and **Approve selected** buttons, plus Deny / Approve (9) for the whole request. **verified** (we haven't clicked any of them yet)
- **The change request can be read through the API** even though the task API can't: `GET https://dataplex.googleapis.com/v1/projects/kc-okf-poc-261122/locations/us/changeRequests/345f4080-...` returns the full request (v1beta1 and v1alpha1 return 404). Fields: `author` = our execution SA, `state: NEW`, labels `source: knowledge_agent`, `generator: enrichment_agent`, `changeType: BATCH_CHANGE_METADATA`, and a list of `createEntryRequest` / `createEntryLinkRequest`. Saved as [03-studio/run1-change-request.json](03-studio/run1-change-request.json). **verified**
- **What is proposed:** a small knowledge base inside the context set, built from Dataplex `document` entries whose text lives in the `overview` aspect (Markdown), the same aspect kcagent writes in step 2. Each page was extracted into [03-studio/run1-proposals/](03-studio/run1-proposals/). **verified**

| Entry id | Document type | Size | What it is |
|---|---|---|---|
| `agents` | knowledge-base-root | 2.2 KB | Front page for agents: what the data is, top 2 traps, how to navigate ("about three searches and three lookups per question") |
| `assets` | knowledge-base-index | 0.3 KB | Folder index |
| `assets/bigquery/kc-okf-poc-261122/ga4_sample` | knowledge-base-index | 0.3 KB | Dataset index |
| `assets/.../ga4_sample/events` | table-context | 5.5 KB | Table page: columns, metric definitions, owner, governance, data quality, usage |
| `documents` | knowledge-base-index | 0.9 KB | Folder index for the 3 topic pages |
| `documents/computing-standard-ecommerce-metrics` | knowledge-base | 3.3 KB | Metric definitions with SQL |
| `documents/data-governance-and-quality-boundaries` | knowledge-base | 8.0 KB | Tiers, retention, finality, attribution rules |
| `documents/pitfalls` | knowledge-base | 5.9 KB | "Pitfalls that silently produce wrong answers" |
| link `events -> events` | entryLink `reference` | | Ties the table page to the real BigQuery table entry in `@bigquery` |

- **Tracer facts: every one of them made it in.** MSC-417, "Merch Store Clickstream", Digital Insights Guild, `#msc-417-data`, 72-hour finality, tiers C1/C2/C3, 14-month retention, engaged session > 10 s, active buyer 28d, net revenue with refunds, `(data deleted)`, `event_date_dt`, 2020-11-01 and 92 days all appear, cited as `[1] Merch Store Clickstream: data policy and metric definitions`. Each fact we spot-checked matches the policy wording, including the on-call steward and "never use local-currency columns". Google's sample docs are cited separately ([2]–[7] in `pitfalls`). **verified** (by grep, plus a manual read of `events`, `agents` and `pitfalls`)
- **One flaw found:** the example SQL in `pitfalls` counts sessions as `COUNT(DISTINCT ga_session_id)` per day, but the same page (and the policy) say a session is `user_pseudo_id` + `ga_session_id`. The page contradicts itself. This makes it a good candidate for the "reject" half of the review test. **verified** (reading)

#### Review test: remove `pitfalls`, approve the rest

![Screenshot 26: Remove proposals for 1 entry? dialog, with pitfalls expanded showing Overview 83% confidence](../docs/screenshots/03-studio/26-remove-pitfalls-confirm.webp)

- **Removing is final:** "You can't undo this. Removed proposals can't be recovered. The proposals are removed from this change request and never applied. Their catalog entries stay as they are." We had already saved the page's full text in [03-studio/run1-proposals/documents__pitfalls.md](03-studio/run1-proposals/documents__pitfalls.md) and the request JSON, so nothing is lost from the record. **verified**
- **Studio's confidence score missed the flaw.** Expanded, `pitfalls` shows **Overview 83%**, "Several independent sources agree on it, and no check holds it back", even though its example SQL contradicts its own session rule. The confidence score looks at whether sources agree, not whether the example SQL is correct. **verified** (screenshot) / the explanation is a **guess**
- Index rows such as `documents` show **N/A** confidence, with the reason text "Enrichment Agent Proposal: Knowledge Base Entry". **verified**

#### After removing `pitfalls`: the proposal viewer

- **The removal worked.** The list now shows **All 8, High 3** (it was 9 and 4), and the viewer pages through "1 of 8" ... "8 of 8". **verified**
- **Confidence per content page:** `events` **86%**, `computing-standard-ecommerce-metrics` **87%**, `data-governance-and-quality-boundaries` **83%**. The reason given is "Every statement traces to a source the run read, which is enough for High." The `agents` front page and the indexes have no score. **verified**
- **What the viewer offers for each proposal** (opened with "View proposal"): **verified**
    - the entry path and type (for example `document · assets/bigquery/kc-okf-poc-261122/ga4_sample/events`) and "2 aspects change": **Overview** (the Markdown text) and **Document aspect** (the `type`/`job` metadata seen in the API JSON)
    - a **New** badge (because it's a Create; an Update would presumably show a diff, which is a **guess** until run 2)
    - **Changes / Preview** toggles: a raw diff or the rendered Markdown
    - a **pencil (edit) icon**: it looks like the reviewer can edit the text before approving, which we haven't tried yet
    - **Remove proposal** on each page, the same as Remove selected in the list
    - **< > arrows** to step through all proposals, like reviewing files in a pull request

![Screenshot 27: proposal viewer 1 of 8, agents front page, rendered preview](../docs/screenshots/03-studio/27-proposal-viewer-agents.webp)

![Screenshot 28: proposal viewer 2 of 8, events table page, Overview 86%, schema columns](../docs/screenshots/03-studio/28-proposal-viewer-events.webp)

![Screenshot 29: proposal viewer 4 of 8, data-governance-and-quality-boundaries, Overview 83%, tiers C1/C2/C3 and how-to-query rules from the made-up policy](../docs/screenshots/03-studio/29-proposal-viewer-data-governance.webp)

#### Approve and publish

![Screenshot 30: run Overview after Approve, status Approved, applying changes, Proposals 8 approved, 0 rejected](../docs/screenshots/03-studio/30-approved-applying-changes.webp)

- **The status went from "Needs review" to "Approved, applying changes"**, and the Proposals card says **"8 approved, 0 rejected"**. The removed `pitfalls` is not counted as "rejected": removing deletes the proposal from the request instead of recording a rejection, so there's no audit trail of what was turned down. (Our local copy is the only record.) **verified**
- **We skipped the optional pencil-edit test**; the published `events` page is byte-for-byte identical to the proposal. **verified**
- **Read back through the API** (the full JSON is saved in [03-studio/run1-change-request-after-approve.json](03-studio/run1-change-request-after-approve.json), with the approver's email redacted): **verified**
    - Change request `state: APPROVED`, `approver` = the user's own account, `author` = `kc-studio-enricher@...`. Its `changes` list now holds 8 items; pitfalls was removed from the request itself.
    - The context set now holds **7 document entries**, all created at 23:51:30 UTC, about 2 seconds after approval (23:51:28), plus the entry link.
    - Aspect keys on the published entries use the project **number** form `655216118709.global.overview` / `.document`. In the proposal they used the name form `dataplex-types.global.overview`. These are the same Google-owned `dataplex-types` project; readers must accept either form.
    - `GET .../entryLinks/link-events-events-776bc352` returns **400 "Operation ... is not allowed for Context Sets"**, so entry links inside a context set can't be read directly with this API.
- **Same person wrote and approved.** The SA is the author and our Owner account approved. Studio didn't stop the person who set up and ran the task from approving its output. We haven't yet tested whether a separate approver identity is *required* or merely *possible* (to do: second account + `roles/dataplex.workflowApprover`). **verified** (no block seen) / the separation question is still open
- **Finding: removing a proposal leaves dangling references.** The published `documents` index still lists `catalog/documents/pitfalls` ("Pitfalls that silently produce wrong answers"), and the `agents` front page still says "3 pages of knowledge". Neither page exists. Studio doesn't regenerate the indexes after you remove one item, so an agent following the index will look up a missing entry. The workaround is to remove or edit the index pages too, or use the pencil to fix them before approving. **verified**

#### Read-back with kcmd 0.2.5

- **Default layout pulls nothing.** `kcmd init --kb kc-okf-poc-261122.us.ga4-merch-context --pull` (run by the user in `results/03-studio/kcmd-kb/`) printed "Warning: Unable to load type information for entry type dataplex-types.global.document. Entries of this type are not pulled. Successfully updated local snapshot." and wrote only `catalog.yaml`. **verified**
- **Why:** `GET projects/dataplex-types/locations/global/entryTypes/document` returns **403 `dataplex.entryTypes.get` denied** (the same for `aspectTypes/document`), while `entryTypes/bigquery-table` in the same Google-owned project reads fine. The `document` type definition isn't readable by our project, probably because it's still Preview-gated (**guess**). kcmd 0.2.5 tolerates a 403 on an *aspect* type ("its aspects are still pulled") but treats a 403 on an *entry* type as fatal for that type (`_loadEntryType` in `build/ts/kcmd/cli.js`). That's a gap in kcmd, and 0.2.5 is the latest version on npm. **verified** (code and API)
- **The OKF layout works.** `kcmd init --kb ... --format okf --pull` reported "Wrote 7 concept(s) to bundle/" and produced `bundle/agents.md`, `assets.md`, `assets/bigquery/kc-okf-poc-261122/ga4_sample.md`, `.../ga4_sample/events.md`, `documents.md`, the two `documents/*.md` pages and `_links.yaml`. Each page is Markdown with YAML front matter: `type` (knowledge-base-root / -index / table-context / knowledge-base) and an `x-kcmd` block that keeps the entry type, parent, labels (`generator: enrichment_agent`) and the Studio job name and time, so `kcmd push` can round-trip it. The entry link to the real BigQuery table is in `_links.yaml`. **verified** (tested in a scratch folder first)
- So **path S1 in [docs/context-layer.md](../docs/context-layer.md) works today**: published Studio context comes out as plain OKF files an outside agent can read, but **only with `--format okf`**. **verified**
- The dangling `pitfalls` row from the removed proposal comes along in `bundle/documents.md`. **verified**
- **There's no `index.md`; the root index is `agents.md`.** Its front matter says `type: knowledge-base-root` and its text starts "Index of the catalog root". The folder indexes are `assets.md`, `documents.md` and `assets/.../ga4_sample.md` (`type: knowledge-base-index`), each sitting next to the folder it describes. kcmd treats `agents.md` and `index.md` as interchangeable root files: when initialising an empty workspace it writes `index.md` unless `agents.md` already exists, and it looks for `<group>_entry.md`, then `agents.md`, then `index.md` as the context set's front page (`build/ts/kcmd/cli.js`). An OKF reader that hard-codes `index.md` must also accept `agents.md`. **verified** (code)

#### Read-back through the kcmd MCP server

`python3 tools/mcp_probe.py results/03-studio/kcmd-okf results/03-studio/kcmd-mcp-probe.md agents assets/bigquery/kc-okf-poc-261122/ga4_sample/events` (run by the user) starts `kcmd mcp` on the OKF workspace and acts like an agent. Full output: [03-studio/kcmd-mcp-probe.md](03-studio/kcmd-mcp-probe.md). **verified**

- **3 tools:** `list-entries` (no inputs), `lookup-entry` (`name`), `modify-entry` (`name, field, updates`). The README also lists `pull` and `push`; 0.2.5 doesn't serve them.
- `list-entries` returns **only the 7 entry names**, with no titles or descriptions, so an agent can't choose a page from the list alone. It has to open `agents` (the root) first and follow the indexes, which is how the root page tells it to navigate.
- `lookup-entry` returns JSON: `name`, `type` (`dataplex-types.global.document`), `resource` (labels, location) and `aspects`. The page text is in `aspects["dataplex-types.global.overview"].content` and is **identical to the `.md` body in the bundle**. The document aspect carries the page role (`table-context`) and the Studio job. The JSON wrapping makes it about 13% bigger than the plain file (6,239 vs 5,526 characters for `events`).
- **There's no tool for entry links**: `_links.yaml` (events page → real BigQuery table) isn't reachable over MCP.
- **Takeaway:** for a read-only question-answering agent, MCP gives the same content as reading the OKF files, plus a write tool you'd need to hide. Reading the files directly (S1) is simpler. MCP earns its place only when the agent can't touch the file system.

#### Who can approve: answered from role definitions (no live second-account test)

The user decided a live test with a second account wasn't needed. These facts come from read-only calls (the API discovery doc, `gcloud iam roles describe`, `GET` on the context set). **verified** unless marked otherwise.

- **Approval is plain IAM, not a Studio setting.** Approving or rejecting needs `dataplex.changeRequests.use`. Roles that have it: `dataplex.workflowApprover` (Beta: get, list, use), `dataplex.workflowAdmin`, `dataplex.catalogAdmin`, `dataplex.admin`, and the basic **Editor** and **Owner** roles.
- **Running Studio doesn't need it.** `dataplex.editor` has `agentTasks.create/run/...` but **no** `changeRequests.use`, and the `content*` roles only have `entryGroups.requestContextChanges`. So **separation of duties is possible**: give task runners `dataplex.editor` + `contentEditor` and reviewers `workflowApprover`. Anyone with basic Editor or Owner can do both, which is what happened in this POC.
- **The context set's approver list is notification only.** The `changeRequestConfig.approverEmails` field (up to 10) is documented as "potential approvers ... notified when a change request is created". It doesn't restrict who can approve (**docs**). Ours is empty (`changeRequestConfig: {}`).
- **Change requests can be scripted**, unlike Studio tasks: `changeRequests.get/list/patch/approve/reject/delete`, with comments on approve and reject (`reviewerComment`, `rejectionComment`), and `entryGroups:requestBatchMetadataChange` to *submit* a reviewed change yourself. That's the API route for hand-written playbooks to go through the same review gate (**docs**, untested).
- **Not tested:** whether the API or console blocks a person from approving a change request they authored themselves.

#### Before versus after, seen in the agent's own SQL

The baseline stage (agent answering without new context) and the final-eval stage (with the new context) both show up as bursts of queries. Counting signals in the SQL text (data queries only, `INFORMATION_SCHEMA` excluded; **verified** counts, **guess** that each burst is the eval answering):

| Signal in the SQL | Baseline (22:16–22:23) | Final eval (22:31–22:38) |
|---|---|---|
| Data queries | 110 | 62 |
| Filter on partition column `event_date_dt` | 54 (49%) | 59 (95%) |
| Scans over 1 GB | 30 | 1 |
| Excludes `(data deleted)` traffic (policy rule) | 0 | 15 |
| Groups by `geo.region` (policy: no city level) | 0 | 3 |
| Uses `geo.city` | 4 | 1 |
| GB billed | 52.7 | 12.5 |

So after enrichment the agent followed our made-up reporting rules and the partition rule, and scanned about 4 times less data. The official scores should be in the run report and change request (next).
