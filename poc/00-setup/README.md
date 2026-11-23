# Step 0: setup commands

Run these one at a time. Results are recorded in [results/00-setup.md](../../results/00-setup.md).

## Local tools

```bash
# nvm (Node version manager), pinned release
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
# open a new shell, then:
nvm install 22
node --version
# bun, pinned release
curl -fsSL https://bun.sh/install | bash -s "bun-v1.2.21"
```

## Cloud (filled in as we go)

```bash
gcloud projects create kc-okf-poc-261122 --name="KC OKF POC"
gcloud billing projects link kc-okf-poc-261122 --billing-account=<BILLING_ACCOUNT_ID>
# Budget: created in the console (Billing > Budgets & alerts), 20, thresholds 50/90/100 %
gcloud services enable dataplex.googleapis.com bigquery.googleapis.com storage.googleapis.com iamcredentials.googleapis.com aiplatform.googleapis.com --project=kc-okf-poc-261122
```

```bash
gcloud config configurations create kc-okf --no-activate
export CLOUDSDK_ACTIVE_CONFIG_NAME=kc-okf && gcloud config set account <YOUR_ACCOUNT> && gcloud config set project kc-okf-poc-261122 && gcloud config set compute/region us-central1
```

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project kc-okf-poc-261122
```
