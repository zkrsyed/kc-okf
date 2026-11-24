# Cloud resources created

Every resource this POC creates, and how to remove it. Remove resources by hand only after review. Deleting the whole project removes everything listed here.

| When | Resource | How to remove |
|---|---|---|
| 2026-11-22 | Project `kc-okf-poc-261122` (number 109873812728), no organization | `gcloud projects delete kc-okf-poc-261122` (30-day recovery window). Removes everything inside the project, but not the budget. |
| 2026-11-22 | Billing link to the user's existing billing account | `gcloud billing projects unlink kc-okf-poc-261122` |
| 2026-11-22 | Budget `kc-okf-poc` (20, alerts at 50/90/100 %) on billing account the user's existing billing account, scoped to this project | Console: Billing > Budgets & alerts > delete. Lives on the billing account, so deleting the project does **not** remove it. |
| 2026-11-22 | BigQuery dataset `ga4_sample` (location US) | `bq rm -r -d kc-okf-poc-261122:ga4_sample` (asks to confirm; removes its tables too) |
| 2026-11-22 | Service account `kc-studio-enricher@kc-okf-poc-261122.iam.gserviceaccount.com` (step 3: Studio's agent runs as it) | `gcloud iam service-accounts delete kc-studio-enricher@kc-okf-poc-261122.iam.gserviceaccount.com` |
| 2026-11-22 | Project IAM: `kc-studio-enricher` gets `serviceusage.serviceUsageConsumer`, `bigquery.dataViewer`, `bigquery.resourceViewer`, `bigquery.jobUser`, `dataplex.catalogViewer`, `dataplex.catalogEditor`, `dataplex.contentEditor` | Removed when the service account is deleted, or per role: `gcloud projects remove-iam-policy-binding kc-okf-poc-261122 --member=serviceAccount:kc-studio-enricher@kc-okf-poc-261122.iam.gserviceaccount.com --role=roles/ROLE` |
| 2026-11-22 | Dataplex service agent identity `service-109873812728@gcp-sa-dataplex.iam.gserviceaccount.com` (created/ensured with `gcloud beta services identity create`) | Google-managed; goes with the project. Nothing to remove. |
| 2026-11-22 | On service account `kc-studio-enricher`: Dataplex service agent gets `roles/iam.serviceAccountTokenCreator` (lets Studio run as our account) | Removed with the service account, or `gcloud iam service-accounts remove-iam-policy-binding kc-studio-enricher@kc-okf-poc-261122.iam.gserviceaccount.com --member=serviceAccount:service-109873812728@gcp-sa-dataplex.iam.gserviceaccount.com --role=roles/iam.serviceAccountTokenCreator` |
| 2026-11-22 | Project IAM: Dataplex service agent gets `roles/bigquery.dataViewer` (Studio docs ask for it on the target data) | `gcloud projects remove-iam-policy-binding kc-okf-poc-261122 --member=serviceAccount:service-109873812728@gcp-sa-dataplex.iam.gserviceaccount.com --role=roles/bigquery.dataViewer` |
| 2026-11-22 | Cloud Storage bucket `gs://kc-okf-poc-261122-signals` (location US): Studio's knowledge signals | `gcloud storage rm -r gs://kc-okf-poc-261122-signals` (removes the files and the bucket) |
| 2026-11-22 | Bucket IAM: `kc-studio-enricher` gets `roles/storage.objectViewer` on `gs://kc-okf-poc-261122-signals` | Removed with the bucket, or `gcloud storage buckets remove-iam-policy-binding gs://kc-okf-poc-261122-signals --member=serviceAccount:kc-studio-enricher@kc-okf-poc-261122.iam.gserviceaccount.com --role=roles/storage.objectViewer` |
| 2026-11-22 | Dataplex context set `ga4-merch-context` (entry group, location `us`), created in the Studio console | Console: Knowledge Studio > Context sets > Delete, or `gcloud dataplex entry-groups delete ga4-merch-context --location=us` (guess: not yet tried) |
| 2026-11-22 | Project IAM: my user account gets `roles/dataplex.contentEditor` (Owner cannot read context sets) | `gcloud projects remove-iam-policy-binding kc-okf-poc-261122 --member=user:YOUR_EMAIL --role=roles/dataplex.contentEditor` |
| 2026-11-22 | Cloud Storage bucket `gs://kc-okf-poc-261122-eval` (US): eval set, kept apart from the signals; `kc-studio-enricher` has `roles/storage.objectViewer` on it | `gcloud storage rm -r gs://kc-okf-poc-261122-eval` |
| 2026-11-22 | Knowledge Studio enrichment task `ga4-events-enrichment` (us-central1), run 1 `d3704062-...` | Console: Knowledge Studio > Enrichments > ga4-events-enrichment > Delete (not scriptable: the agentTasks API has IAM methods only) |
| 2026-11-22 | Change request `345f4080-...` (state APPROVED) and the 7 published document entries + 1 entry link inside `ga4-merch-context` | Removed with the context set (guess); entries can also be deleted one by one from the console |
| 2026-11-23 | Context set entry `documents/playbook-final-daily-net-revenue` (pushed with `kcmd push`, step 4); the `documents` and `agents` entries were updated by the same push | Removed with the context set (guess); or delete the page in the console |
| 2026-11-23 | Change request `919699e7-...` (state NEW, authored by the user: the engaged-sessions playbook, never approved) | `curl -X DELETE .../changeRequests/919699e7-aa2f-42d9-9bb5-d1f1f8e4ee3b` (an author can delete a NEW request with `dataplex.changeRequests.delete`; guess, not tried) |
| 2026-11-24 | Dataplex context set `ga4-merch-context-r2` (us), created in the console for Studio run 2 (step 7) | Console: Knowledge Studio > Context sets > Delete (needs `dataplex.contentAdmin`) |
| 2026-11-24 | Knowledge Studio enrichment task `ga4-events-enrichment-r2` (us-central1), run `94165469-...` | Console: Knowledge Studio > Enrichments > ga4-events-enrichment-r2 > Delete |
| 2026-11-24 | Change request `9b4cc44a-...` (APPROVED) and its 7 document entries + 1 entry link in `ga4-merch-context-r2` | Removed with the context set (guess) |

**Remember:** Google's OKF connector demo creates a project-wide `okf` aspect type that its cleanup script does not remove.

## Local changes to undo when done

- `gcloud auth application-default set-quota-project YOUR_PREVIOUS_QUOTA_PROJECT` (ADC quota project was switched to the POC project).
- `gcloud config configurations delete kc-okf` (local gcloud profile).
- `~/.npmrc`: original saved as `trash/npmrc.backup` (it had `prefix=~/.npm-global`).
