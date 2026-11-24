# Description accuracy: 30 fixed fields, run 1 vs run 2

Google's text: [google-schema-30-fields.md](google-schema-30-fields.md) (**docs**). Studio's text is taken from the proposed table page (`events`) of each run, which is the only place either run describes columns: run 1 [run1-proposals/…events.md](../03-studio/run1-proposals/assets__bigquery__kc-okf-poc-261122__ga4_sample__events.md), run 2 [run2-proposals/…events.md](run2-proposals/assets__bigquery__kc-okf-poc-261122__ga4_sample__events.md). A parent record's description doesn't count for its child field. Marks are mine (**verified** reading, judgement as stated in the reference file).

| # | Field | Run 1 text | Run 1 | Run 2 text | Run 2 |
|---|---|---|---|---|---|
| 1 | `event_date` | Date of the event. | vague (no YYYYMMDD format) | Date of the event formatted as a text string. | vague (no YYYYMMDD format) |
| 2 | `event_params.key` | – | not described | – | not described |
| 3 | `event_params.value.int_value` | – | not described | – | not described |
| 4 | `event_value_in_usd` | (listed, no text) | not described | Monomorphic event value. | vague (meaningless; doesn't say USD-converted "value" parameter) |
| 5 | `user_pseudo_id` | (listed, no text) | not described | Tier C2 (pseudonymous) personal data; the pseudonymized client cookie or device-instance identifier. | right |
| 6 | `privacy_info.uses_transient_token` | – | not described | – | not described |
| 7 | `user_properties.value` | – | not described | – | not described |
| 8 | `user_properties.value.double_value` | – | not described | – | not described |
| 9 | `user_ltv.revenue` | – | not described | – | not described |
| 10 | `device.mobile_brand_name` | – | not described | – | not described |
| 11 | `device.mobile_os_hardware_model` | – | not described | – | not described |
| 12 | `device.advertising_id` | – | not described | – | not described |
| 13 | `device.web_info` | – | not described | – | not described |
| 14 | `geo` | (listed, no text) | not described | Geolocation attributes determined from client network endpoints. | right |
| 15 | `geo.region` | – | not described | "Other `geo.*` fields: standard regional and country geographic descriptors." | vague |
| 16 | `app_info.id` | – | not described | – | not described |
| 17 | `app_info.install_source` | – | not described | – | not described |
| 18 | `traffic_source.name` | – | not described | – | not described |
| 19 | `event_dimensions` | (listed, no text) | not described | Operational dimensions accompanying the event record. | vague (it holds `hostname`) |
| 20 | `ecommerce.purchase_revenue_in_usd` | named inside `ecommerce`, no text | not described | Total gross purchase revenue recorded in USD. | right |
| 21 | `ecommerce.refund_value` | – | not described | – | not described |
| 22 | `ecommerce.tax_value` | – | not described | – | not described |
| 23 | `items.item_id` | – | not described | – | not described |
| 24 | `items.item_category` | – | not described | – | not described |
| 25 | `items.item_category4` | – | not described | – | not described |
| 26 | `items.quantity` | – | not described | – | not described |
| 27 | `items.item_refund` | – | not described | – | not described |
| 28 | `items.item_list_id` | – | not described | – | not described |
| 29 | `items.promotion_id` | – | not described | – | not described |
| 30 | `event_date_dt` | Date-typed event date column configured as the table's partition column. | right | Date-typed representation of the event partition, used for partition-pruning filters. | right |

| | Right | Vague | Wrong | Not described |
|---|---|---|---|---|
| Run 1 | 1 | 1 | 0 | 28 |
| Run 2 | 4 | 4 | 0 | 22 |

Nothing was wrong, but almost everything below the top level was left out: of the 24 nested fields in the sample, run 2 described 2 (`ecommerce.purchase_revenue_in_usd`, and `geo.region` only vaguely as part of "other geo.* fields").
