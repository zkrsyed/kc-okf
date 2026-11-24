| Setup | Pass | Held-out (13-15) | Partition filter | Avg tool calls | Avg context reads | Avg input tokens | Avg seconds | GB billed |
|---|---|---|---|---|---|---|---|---|
| B2: run 2 context as OKF files | **12/15** | 3/3 | 14/15 | 18.1 | 9.6 | 133,347 | 127 | 24.16 |
| C2: run 2 context via kcmd MCP | **12/15** | 3/3 | 13/15 | 13.3 | 4.8 | 169,731 | 130 | 26.11 |

| Q | Question | B2: run 2 context as OKF files | C2: run 2 context via kcmd MCP |
|---|---|---|---|
| 1 | How many sessions are in the events table in total? | ✅ pass | ✅ pass |
| 2 | How many daily active users were there each day in December 2020? | ❌ no final answer | ✅ pass |
| 3 | Which 10 products were added to the cart most often? | ✅ pass | ❌ no final answer |
| 4 | Which pages got the most page views on 15 January 2021? | ❌ 10 of top 10 rows not in golden | ✅ pass |
| 5 | How many purchases were made each day in the first week of January 2021? | ✅ pass | ✅ pass |
| 6 | What was net merch revenue for December 2020? | ✅ pass | ✅ pass |
| 7 | How many active buyers (28d) were there as of 31 January 2021? | ✅ pass | ✅ pass |
| 8 | Show the number of users by city for January 2021. | ✅ pass | ✅ pass |
| 9 | Break down January 2021 sessions by traffic source for a marketing attribution report. | ❌ 8 rows, golden 4 | ❌ 8 rows, golden 4 |
| 10 | What was the cart conversion rate in December 2020? | ✅ pass | ✅ pass |
| 11 | How many engaged sessions were there in January 2021? | ✅ pass | ❌ no final answer |
| 12 | Show daily net merch revenue for January 2021, final days only. | ✅ pass | ✅ pass |
| 13* | Break down December 2020 sessions by traffic medium for a marketing attribution report. | ✅ pass | ✅ pass |
| 14* | Which 5 cities had the most purchasers in December 2020? | ✅ pass | ✅ pass |
| 15* | What was total net merch revenue for January 2021, counting only days that are final? | ✅ pass | ✅ pass |

\* held-out question: not in Studio's eval set, so Studio never optimised for it.
