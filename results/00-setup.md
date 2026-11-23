# Step 0: setup, results

## Decisions

| Item | Choice | Why |
|---|---|---|
| GCP project | new project `kc-okf-poc-261122` | Deleting the project removes everything, including the project-wide `okf` aspect type |
| Billing account | the user's existing billing account (the only open one) | |
| Budget alert | 20 USD, alerts at 50 / 90 / 100 % | |
| Dataset | `bigquery-public-data.ga4_obfuscated_sample_ecommerce` | Google's OKF repo already has a sample bundle for it; its nested schema tests capability 7 |
| Catalog location | `us` (where the public datasets live) | |
| Vertex AI and task execution region | `us-central1` | |
| Knowledge signals | Cloud Storage files only | |
| Policy document | a short made-up sensitivity/PII policy | No private policy is used |
| Working copy of data | copy 3 daily `events_YYYYMMDD` tables into our own dataset `ga4_sample` (location `us`) | So `kcmd push` and Studio work on tables we own, and results are visible in the console. Removes the "can Studio target public data?" risk. |

## Local tools (verified, 2026-11-22)

| Tool | Version |
|---|---|
| gcloud | 588.0.0 |
| Python | 3.12.3 |
| uv | 0.12.18 |
| git | 2.43.0 |
| gh | 2.45.0 |
| Node | 22.23.5 (via nvm 0.40.3), npm 10.9.9 |
| bun | 1.2.21 (needed `unzip` 6.0 from apt) |
| kcmd | `@google-cloud/kcmd` 0.2.5 (build `4b42d81`), pinned in [package.json](../package.json) and `package-lock.json`. Last published 2026-11-11, so a machine that blocks very new packages may refuse it for a while. `npm audit`: 3 moderate advisories in its dependencies `glob` and `minimatch` (file-pattern libraries); acceptable for a local POC. |

## What the docs say Studio enrichment needs (docs, read 2026-11-22)

Sources: [configure-enrichment-prerequisites][P], [create-enrichment-tasks][C], [context-sets][X], [about-enrichment-tasks][A]. All are Preview pages.

**APIs** ([P]): `dataplex`, `bigquery`, `storage`, `iamcredentials`. Vertex AI (`aiplatform`) is **not** on Studio's list; we need it only for `kcagent` and our own agent.

**Three identities** (like three Windows accounts on one service):

| Who | Roles (docs) |
|---|---|
| **Me** (creates and runs the task) | `roles/dataplex.dataScanEditor` or `roles/dataplex.editor`; `roles/iam.serviceAccountUser` on the execution service account |
| **Execution service account** (a robot account I create; the agent runs as it) | `roles/serviceusage.serviceUsageConsumer`, `roles/bigquery.dataViewer`, `roles/dataplex.contentEditor`, `roles/dataplex.catalogEditor`, `roles/dataplex.catalogViewer`; recommended `roles/bigquery.resourceViewer`; `roles/bigquery.jobUser` (the pages disagree on whether it is required); `roles/storage.objectViewer` on the input bucket |
| **Dataplex service agent** (`service-PROJECT_NUMBER@gcp-sa-dataplex.iam.gserviceaccount.com`, Google-owned) | `roles/iam.serviceAccountTokenCreator` on the execution service account (so it can act as it); `roles/bigquery.dataViewer` on the target data |
| **Approver** | `roles/dataplex.contentEditor` on the context set, `roles/dataplex.catalogViewer`, and `roles/dataplex.workflowApprover` ("Required to approve and publish change requests") |

**Locations** ([C], [X]): a context set can be regional, multi-regional (`us`, `eu`) or global. A multi-region `us` context set picks an execution region such as `us-central1`. Target tables must be compatible with the context set's location. So: **context set in `us`, task runs in `us-central1`**.

**Inputs** ([P], [C]): Cloud Storage files in Markdown, plain text, PDF, HTML or CSV, plus SQL and dbt files. The evaluation set is JSONL, one line per question: `evaluation_request.prompt.text` and `evaluation_request.golden_response.text` (the SQL). A Gemini autorater checks whether the SQL means the same.

**Limits** ([A], [C]): one enrichment task per context set; at most 500 tables per task; a run takes 20 to 60 minutes; logs can lag 20 to 30 minutes; free during Preview apart from BigQuery and storage use.

## Open risks (guess)

- **Public dataset as a target.** None of the four pages say whether a task can target `bigquery-public-data`. The service agent may need `bigquery.dataViewer` on the dataset, which we cannot grant on Google's project (public data is readable by any authenticated user, which may be enough). Fallback: copy the tables into a dataset in our own `us` project (size not checked yet; we will check it with a free metadata query before copying).
- **Author and publisher separation.** No page says whether the approver must differ from the author. To test in step 3 with a second identity.
- **`roles/bigquery.jobUser`.** One page lists it as required and another as optional. We grant it to avoid a failed run.

[P]: https://docs.cloud.google.com/knowledge-catalog/docs/configure-enrichment-prerequisites
[C]: https://docs.cloud.google.com/knowledge-catalog/docs/create-enrichment-tasks
[X]: https://docs.cloud.google.com/knowledge-catalog/docs/context-sets
[A]: https://docs.cloud.google.com/knowledge-catalog/docs/about-enrichment-tasks

## Cloud setup (verified, 2026-11-22)

| Step | Result |
|---|---|
| Project | `kc-okf-poc-261122` created, ACTIVE, no organization |
| Billing | linked to the user's existing billing account, `billingEnabled: true` |
| Budget | `kc-okf-poc`, 20, alerts at 50/90/100 % (created in the console) |
| APIs enabled by us | `dataplex`, `bigquery`, `storage`, `iamcredentials`, `aiplatform` |
| APIs Google turned on with them | `analyticshub`, `bigqueryconnection`, `bigquerydatapolicy`, `bigquerydatatransfer`, `bigquerymigration`, `bigqueryreservation`, `bigquerystorage`, `dataform`, `datastore`, `logging`, `monitoring`, `cloudtrace`, `telemetry`, `storage-api`, `storage-component` and others: dependencies or project defaults, free to have on |
| Compute API | `compute.googleapis.com` was enabled by a gcloud prompt when setting `compute/region` (gcloud checks the region against the Compute API). Free to have on; nothing runs. |
| gcloud profile | configuration `kc-okf`: account set, `project = kc-okf-poc-261122`, `compute/region = us-central1`. Default profile unchanged. Pick it with `export CLOUDSDK_ACTIVE_CONFIG_NAME=kc-okf`. |
| Library credentials (ADC) | refreshed for the same account; quota project `kc-okf-poc-261122`; token check OK. Shared by all profiles: restore with `gcloud auth application-default set-quota-project YOUR_PREVIOUS_QUOTA_PROJECT` when done. |

## Step 0 status

Done. The execution service account and IAM roles for Studio are created in step 3, where they are used.
