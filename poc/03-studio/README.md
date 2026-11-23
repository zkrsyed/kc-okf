# Step 3: Knowledge Studio, commands

Everything we ran for step 3, in order. Results and findings: [results/03-studio.md](../../results/03-studio.md). How to remove each resource: [results/cloud-resources.md](../../results/cloud-resources.md).

Every command assumes the gcloud profile for this POC: run `export CLOUDSDK_ACTIVE_CONFIG_NAME=kc-okf` once per terminal tab. Replace `YOUR_EMAIL` with your own Google account. The project number `109873812728` names the Dataplex service agent; use your own project's number.

## 3a. Identity that Studio runs as ("Run as" service account)

```bash
# our execution service account
gcloud iam service-accounts create kc-studio-enricher --display-name="KC Studio enrichment (POC)"
```

```bash
# its project roles: use the API quota, read and query BigQuery, read and write catalog metadata and context
for r in serviceusage.serviceUsageConsumer bigquery.dataViewer bigquery.resourceViewer bigquery.jobUser dataplex.catalogViewer dataplex.catalogEditor dataplex.contentEditor; do echo "== $r"; gcloud projects add-iam-policy-binding kc-okf-poc-261122 --member="serviceAccount:kc-studio-enricher@kc-okf-poc-261122.iam.gserviceaccount.com" --role="roles/$r" --condition=None --format=none; done
```

```bash
# make sure Google's Dataplex service agent exists in the project (needs gcloud beta)
gcloud beta services identity create --service=dataplex.googleapis.com
```

```bash
# let the service agent act as our service account (the "badge swap")
gcloud iam service-accounts add-iam-policy-binding kc-studio-enricher@kc-okf-poc-261122.iam.gserviceaccount.com --member="serviceAccount:service-109873812728@gcp-sa-dataplex.iam.gserviceaccount.com" --role="roles/iam.serviceAccountTokenCreator" --format=none
```

```bash
# the service agent also reads BigQuery data
gcloud projects add-iam-policy-binding kc-okf-poc-261122 --member="serviceAccount:service-109873812728@gcp-sa-dataplex.iam.gserviceaccount.com" --role="roles/bigquery.dataViewer" --condition=None --format=none
```

## 3b. Knowledge signals (documents Studio reads)

Contents: Google's 8 sample docs (`signals/google-sample/`) and our made-up policy doc `signals/merch-store-data-policy.md`, which carries the tracer facts.

```bash
gcloud storage buckets create gs://kc-okf-poc-261122-signals --location=US --uniform-bucket-level-access
```

```bash
cd ~/apps/kc-okf && gcloud storage cp -r poc/03-studio/signals/* gs://kc-okf-poc-261122-signals/
```

```bash
gcloud storage buckets add-iam-policy-binding gs://kc-okf-poc-261122-signals --member="serviceAccount:kc-studio-enricher@kc-okf-poc-261122.iam.gserviceaccount.com" --role="roles/storage.objectViewer"
```

## 3c. Let yourself read context (Owner alone can't)

```bash
gcloud projects add-iam-policy-binding kc-okf-poc-261122 --member="user:YOUR_EMAIL" --role="roles/dataplex.contentEditor" --condition=None --format=none
```

## 3d. Evaluation set (kept apart from the signals so Studio can't learn the answers)

The format of each line of `eval-set.jsonl`: `{"evaluation_request": {"prompt": {"text": "..."}, "golden_response": {"text": "<golden SQL>"}}}`. The golden SQL comes from `eval-sql/01.sql`–`12.sql`; we dry-ran each one first (`eval-sql/dry-run.txt`).

```bash
gcloud storage buckets create gs://kc-okf-poc-261122-eval --location=US --uniform-bucket-level-access
```

```bash
cd ~/apps/kc-okf && gcloud storage cp poc/03-studio/eval-set.jsonl gs://kc-okf-poc-261122-eval/
```

```bash
gcloud storage buckets add-iam-policy-binding gs://kc-okf-poc-261122-eval --member="serviceAccount:kc-studio-enricher@kc-okf-poc-261122.iam.gserviceaccount.com" --role="roles/storage.objectViewer" --format=none
```

## 3e. Console only (no API for these)

These steps have no public API (`agentTasks` has IAM methods only), so they're done in **Knowledge Catalog > Studio**:

1. **Context sets > Create**: name `ga4-merch-context`, location **multi-region `us`** (at the top of the list; the default is us-central1).
2. **Enrichments > Create**, a 4-page wizard:
    - **Define:** name `ga4-events-enrichment`
    - **Scope:** context set `ga4-merch-context`, region us-central1, resource the BigQuery table `ga4_sample.events`, knowledge signal the bucket `kc-okf-poc-261122-signals`
    - **Improve:** evaluation set `gs://kc-okf-poc-261122-eval/eval-set.jsonl`; no curation set; auto-publish off; self-learning off
    - **Run:** Run as `kc-studio-enricher@...`, trigger On demand
3. **Wait about 5 minutes** after Create (the task is created in the background), then **Run now**. It ran for 29 minutes.
4. **Review:** open the run, read each proposal with **View proposal**, remove `pitfalls` (**Remove selected**), then **Approve**.

## 3f. Read-only checks we used

```bash
# the run's own event log -> results/03-studio/run1-agent-log.{jsonl,md}
cd ~/apps/kc-okf && python3 tools/export_run_log.py d3704062-699a-4661-9299-1d42e5d4266d results/03-studio/run1-agent-log
```

```bash
# the change request with every proposed page (the API can read and approve change requests, unlike tasks)
curl -s -H "Authorization: Bearer $(gcloud auth print-access-token)" -H "x-goog-user-project: kc-okf-poc-261122" "https://dataplex.googleapis.com/v1/projects/kc-okf-poc-261122/locations/us/changeRequests/345f4080-d80d-4ae6-85ce-a856cda1ae23"
```

```bash
# BigQuery jobs the service account ran (audit log)
gcloud logging read 'protoPayload.methodName="jobservice.jobcompleted" AND protoPayload.authenticationInfo.principalEmail="kc-studio-enricher@kc-okf-poc-261122.iam.gserviceaccount.com"' --freshness=2d --format=json
```

## 3g. Read the published context back

kcmd 0.2.5 from the step 2 install. The default layout pulls nothing (403 on the `document` type definition); use `--format okf`.

```bash
cd ~/apps/kc-okf && mkdir -p results/03-studio/kcmd-okf && cd results/03-studio/kcmd-okf && ../../../vendor/knowledge-catalog/toolbox/enrichment/node_modules/.bin/kcmd init --kb kc-okf-poc-261122.us.ga4-merch-context --format okf --pull && find . -type f | sort
```

```bash
# act as an MCP client against `kcmd mcp` (read tools only)
cd ~/apps/kc-okf && python3 tools/mcp_probe.py results/03-studio/kcmd-okf results/03-studio/kcmd-mcp-probe.md agents assets/bigquery/kc-okf-poc-261122/ga4_sample/events
```
