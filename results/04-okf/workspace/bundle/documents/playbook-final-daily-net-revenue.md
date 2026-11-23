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
# Playbook: daily net revenue, final days only

Hand-written by the data team (POC step 4). Follow this when a question asks for revenue **per day** over a period that reaches the end of the data.

## When to use

Questions like "daily net revenue for January", "revenue trend last month by day", "net sales per day up to the latest date".

## Approach

1. Net merch revenue = `SUM(ecommerce.purchase_revenue_in_usd) - SUM(IFNULL(ecommerce.refund_value_in_usd, 0))`. USD columns only. Treat a missing refund as 0, or the whole day becomes NULL.
2. A day is final 72 hours after it ends, so **drop the last 3 days** of the period: end the range at `DATE_SUB(<last day>, INTERVAL 3 DAY)`. The data ends on 2021-01-31, so January's final days are 2021-01-01 to 2021-01-28.
3. Filter on the partition column `event_date_dt`, never on the string `event_date`.
4. Group by `event_date_dt` and order by it.
5. In the answer, say that the last 3 days were left out because they are not final yet.

## SQL

```sql
SELECT event_date_dt,
       SUM(ecommerce.purchase_revenue_in_usd) - SUM(IFNULL(ecommerce.refund_value_in_usd, 0)) AS net_merch_revenue_usd
FROM `kc-okf-poc-261122.ga4_sample.events`
WHERE event_date_dt BETWEEN '2021-01-01' AND DATE_SUB('2021-01-31', INTERVAL 3 DAY)
GROUP BY event_date_dt
ORDER BY event_date_dt
```

## Traps seen before

- Using `purchase_revenue` (local currency) instead of `purchase_revenue_in_usd`.
- Forgetting `IFNULL` on refunds, which turns days without refunds into NULL.
- Including 2021-01-29 to 2021-01-31, which are not final.
