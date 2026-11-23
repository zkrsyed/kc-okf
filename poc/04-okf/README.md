# Step 4: OKF and hand-written playbooks, commands

Results: [results/04-okf.md](../../results/04-okf.md). Run with `export CLOUDSDK_ACTIVE_CONFIG_NAME=kc-okf`; `KCMD=~/apps/kc-okf/vendor/knowledge-catalog/toolbox/enrichment/node_modules/.bin/kcmd` (0.2.5, Node 22 via nvm).

## 4a. The OKF spec and sample bundles (read-only)

```bash
cd ~/apps/kc-okf/vendor
git clone https://github.com/GoogleCloudPlatform/open-knowledge-format            # deprecated 2026-11-18, at 8a8ff87
git clone https://github.com/open-knowledge-format/open-knowledge-format okf-v03  # v0.3 spec, at 527e81a
```

## 4b. Compare bundles with the spec

```bash
cd ~/apps/kc-okf
uv run tools/okf_check.py results/04-okf/pull-after-push/bundle results/04-okf/okf-check-kc-bundle.md
uv run tools/okf_check.py vendor/okf-v03/bundles/ga4 results/04-okf/okf-check-google-ga4-bundle.md
```

## 4c. Hand-written playbook through `kcmd push` (direct write, no review)

The workspace is a copy of the step 3 pull (`results/03-studio/kcmd-okf`). Add a page under `bundle/documents/`, with this frontmatter (the `document` aspect is required, or the push fails for that page):

```yaml
---
type: knowledge-base
x-kcmd:
  v: 1
  entryType: projects/dataplex-types/locations/global/entryTypes/document
  parentEntry: projects/kc-okf-poc-261122/locations/us/entryGroups/ga4-merch-context/entries/documents
  entrySource:
    location: us
    labels:
      source: human
  aspects:
    dataplex-types.global.document: {}
---
```

```bash
cd ~/apps/kc-okf/results/04-okf/workspace
$KCMD push --dry-run     # shows creates / updates, sends nothing
$KCMD push               # writes directly to the context set
```

```bash
# round trip: pull into a fresh folder and compare
mkdir -p ~/apps/kc-okf/results/04-okf/pull-after-push && cd ~/apps/kc-okf/results/04-okf/pull-after-push
$KCMD init --kb kc-okf-poc-261122.us.ga4-merch-context --format okf --pull
diff -r ../workspace/bundle bundle
```

## 4d. Hand-written playbook through a change request (reviewed)

`request.json` wraps one `createEntryRequest` (entry type `document`, the `document` aspect with `type: knowledge-base`, and the Markdown in the `overview` aspect) in `changePayload`: see [results/04-okf/reviewed-route/request.json](../../results/04-okf/reviewed-route/request.json).

```bash
cd ~/apps/kc-okf && T=$(gcloud auth print-access-token)
curl -s -X POST -H "Authorization: Bearer $T" -H "x-goog-user-project: kc-okf-poc-261122" -H "Content-Type: application/json" \
  "https://dataplex.googleapis.com/v1/projects/kc-okf-poc-261122/locations/us/entryGroups/ga4-merch-context:requestBatchMetadataChange" \
  -d @results/04-okf/reviewed-route/request.json
```

```bash
# approving your own request is refused with 403 "not authorized to approve their own ChangeRequest"
curl -s -X POST -H "Authorization: Bearer $T" -H "x-goog-user-project: kc-okf-poc-261122" -H "Content-Type: application/json" \
  "https://dataplex.googleapis.com/v1/projects/kc-okf-poc-261122/locations/us/changeRequests/919699e7-aa2f-42d9-9bb5-d1f1f8e4ee3b:approve" \
  -d '{"comment":"reviewed"}'
```
