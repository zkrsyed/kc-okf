# Step 2: kcagent (Google's sample enrichment agent), commands

Source: `GoogleCloudPlatform/knowledge-catalog`, `toolbox/enrichment`, pinned at commit `6886cc6` (2026-11-21).
The checkout lives in `vendor/` (git-ignored); only our inputs and outputs are committed.

```bash
# 2a. clone at a pinned commit
git clone https://github.com/GoogleCloudPlatform/knowledge-catalog ~/apps/kc-okf/vendor/knowledge-catalog
cd ~/apps/kc-okf/vendor/knowledge-catalog && git checkout 6886cc6
```

```bash
# 2b. use the published kcmd instead of the unbuilt ../mdcode, then build
cd ~/apps/kc-okf/vendor/knowledge-catalog/toolbox/enrichment
npm pkg set "dependencies.@google-cloud/kcmd=0.2.5" && npm install
mv node_modules/@google-cloud/kcmd ~/apps/kc-okf/trash/kcmd-symlink   # npm kept a link to ../mdcode
npm install --save-exact @google-cloud/kcmd@0.2.5
npm run build            # -> dist/kcagent, dist/md-fileset

# 2d. run (from each run folder; uses the kc-okf gcloud profile for project + Vertex region)
cd ~/apps/kc-okf/results/02-kcagent/run1
CLOUDSDK_ACTIVE_CONFIG_NAME=kc-okf ../../../vendor/knowledge-catalog/toolbox/enrichment/dist/kcagent enrich --catalog-path . --tools-path tools --prompt-path prompt.md
```
