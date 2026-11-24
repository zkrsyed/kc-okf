# Step 7 commands: Studio run 2 (custom instruction)

Run from the repo root with the gcloud profile active: `export CLOUDSDK_ACTIVE_CONFIG_NAME=kc-okf`. Results: [results/07-studio-run2.md](../../results/07-studio-run2.md).

## 7a. Console (no API for tasks)

1. **Context sets > Create:** `ga4-merch-context-r2`, location multi-region `us`.
2. **Enrichments > Create enrichment task:** `ga4-events-enrichment-r2`. Every setting is the same as run 1 ([step 3](../03-studio/README.md)) except *Custom instructions*:

    ```text
    For every column and nested field of the events table, write a description and record its sensitivity tier and whether it is personal data, as stated in the data policy. Also propose business glossary terms with definitions for the policy's metrics and concepts, and state each data rule from the policy as its own item.
    ```

3. **Create**, open the task, **Run now** (Create doesn't start a run). Review and approve the change request in the run page when it says *Needs review*.

## 7b. Read what the run produced (read-only)

```bash
# run log from Cloud Logging
python3 tools/export_run_log.py 94165469-4f79-4922-ab13-83c9b2bb1d77 results/07-studio-run2/run2-agent-log

# the change request (proposals) before and after approval
T=$(gcloud auth print-access-token)
curl -s -H "Authorization: Bearer $T" "https://dataplex.googleapis.com/v1/projects/kc-okf-poc-261122/locations/us/changeRequests/9b4cc44a-6806-44ff-8861-8f02cf21fa0f" > results/07-studio-run2/run2-change-request.json

# snapshot: every entry and aspect, entry links, glossaries, and the BigQuery table's column descriptions
python3 tools/dump_context_set.py ga4-merch-context-r2 results/07-studio-run2/run2-snapshot
python3 tools/dump_context_set.py ga4-merch-context    results/07-studio-run2/run1-snapshot
```

BigQuery jobs of the run: `bq ls -j -a` for the window 19:38–20:13 UTC, filtered to `kc-studio-enricher` ([run2-bq-jobs.csv](../../results/07-studio-run2/run2-bq-jobs.csv)). Studio's eval and confidence numbers are only in the console (run page, tabs *Evaluation* and *Artifacts*).

## 7c. Agent test on run 2's context (B2, C2)

```bash
# pull run 2's context set as OKF files (Node 22 via nvm)
KCMD=$PWD/vendor/knowledge-catalog/toolbox/enrichment/node_modules/.bin/kcmd
mkdir -p results/07-studio-run2/kcmd-okf && cd results/07-studio-run2/kcmd-okf
$KCMD init --kb kc-okf-poc-261122.us.ga4-merch-context-r2 --format okf --pull
cd ../../..
```

```bash
# run setups B and C of step 5 against this bundle; results go to results/07-studio-run2/agent as B2 and C2
cd poc/05-agent
export KC_BUNDLE=$HOME/apps/kc-okf/results/07-studio-run2/kcmd-okf KC_RUNS_DIR=results/07-studio-run2/agent KC_TAG=2
uv run python -W ignore run_all.py B > ../../results/07-studio-run2/agent/progress-B2.log 2>&1 &
uv run python -W ignore run_all.py C > ../../results/07-studio-run2/agent/progress-C2.log 2>&1 &
wait
KC_RUNS_DIR=results/07-studio-run2/agent uv run python -W ignore score.py
```

The three `KC_*` variables are optional; without them the harness behaves exactly as in step 5.
