| Setup | Pass | Held-out (13-15) | Partition filter | Avg tool calls | Avg context reads | Avg input tokens | Avg seconds | GB billed |
|---|---|---|---|---|---|---|---|---|
| A: no context | **6/15** | 0/3 | 9/15 | 12.7 | 0.0 | 68,448 | 78 | 44.90 |
| B: KC context as OKF files | **10/15** | 3/3 | 14/15 | 17.5 | 9.9 | 150,026 | 92 | 16.60 |
| C: KC context via kcmd MCP | **12/15** | 3/3 | 15/15 | 12.5 | 5.3 | 429,638 | 190 | 14.85 |

| Q | Question | A: no context | B: KC context as OKF files | C: KC context via kcmd MCP |
|---|---|---|---|---|
| 1 | How many sessions are in the events table in total? | ✅ pass | ✅ pass | ✅ pass |
| 2 | How many daily active users were there each day in December 2020? | ✅ pass | ❌ no final answer | ✅ pass |
| 3 | Which 10 products were added to the cart most often? | ✅ pass | ❌ 10 of top 10 rows not in golden | ✅ pass |
| 4 | Which pages got the most page views on 15 January 2021? | ✅ pass | ❌ 3 of top 10 rows not in golden | ❌ 10 of top 10 rows not in golden |
| 5 | How many purchases were made each day in the first week of January 2021? | ✅ pass | ✅ pass | ✅ pass |
| 6 | What was net merch revenue for December 2020? | ❌ no final answer | ✅ pass | ✅ pass |
| 7 | How many active buyers (28d) were there as of 31 January 2021? | ✅ pass | ✅ pass | ✅ pass |
| 8 | Show the number of users by city for January 2021. | ❌ policy broken: uses geo\.city | ❌ 10 rows, golden 109 | ✅ pass |
| 9 | Break down January 2021 sessions by traffic source for a marketing attribution report. | ❌ 95 rows, golden 4 | ❌ 8 rows, golden 4 | ❌ 8 rows, golden 4 |
| 10 | What was the cart conversion rate in December 2020? | ❌ golden 0.25041420118343194, agent first row [1586.0, 8450.0, 18.77, 15 | ✅ pass | ✅ pass |
| 11 | How many engaged sessions were there in January 2021? | ❌ golden 106301.0, agent first row [111119.0] | ✅ pass | ❌ golden 106301.0, agent first row [111119.0] |
| 12 | Show daily net merch revenue for January 2021, final days only. | ❌ no final answer | ✅ pass | ✅ pass |
| 13* | Break down December 2020 sessions by traffic medium for a marketing attribution report. | ❌ golden row ['(data deleted)', 138.0] not found | ✅ pass | ✅ pass |
| 14* | Which 5 cities had the most purchasers in December 2020? | ❌ policy broken: uses geo\.city | ✅ pass | ✅ pass |
| 15* | What was total net merch revenue for January 2021, counting only days that are final? | ❌ no final answer | ✅ pass | ✅ pass |

\* held-out question: not in Studio's eval set, so Studio never optimised for it.
