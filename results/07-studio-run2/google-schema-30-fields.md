# Reference: Google's descriptions for the 30 sample fields

Source: Google Analytics Help, "BigQuery Export schema", https://support.google.com/analytics/answer/7029846 (read 2026-11-24; the page shows no "last updated" date). Used to mark Studio's descriptions in run 2 as right, vague or wrong. **docs**

Two rows are paraphrased in part, because the fetch tool shortened long quotes; they're marked.

| # | Field | Google's description |
|---|---|---|
| 1 | `event_date` | The date when the event was logged (YYYYMMDD format in the registered timezone of your app). |
| 2 | `event_params.key` | The name of the event parameter. |
| 3 | `event_params.value.int_value` | If the event parameter is represented by an integer, it is populated in this field. |
| 4 | `event_value_in_usd` | The currency-converted value (in USD) of the event's "value" parameter. |
| 5 | `user_pseudo_id` | The pseudonymous id (e.g., app instance ID) for the user. *(paraphrased rest: a unique ID assigned when the user first opens the app or visits the site)* |
| 6 | `privacy_info.uses_transient_token` | Whether a web user has denied Analytics storage and the developer has enabled measurement without cookies… *(shortened; values Yes, No, Unset)* |
| 7 | `user_properties.value` | A record for the user property value. |
| 8 | `user_properties.value.double_value` | The double value of the user property. |
| 9 | `user_ltv.revenue` | The Lifetime Value (revenue) of the user. This field is not populated in intraday tables. |
| 10 | `device.mobile_brand_name` | The device brand name. |
| 11 | `device.mobile_os_hardware_model` | The device model information retrieved directly from the operating system. |
| 12 | `device.advertising_id` | Advertising ID/IDFA. |
| 13 | `device.web_info` | Not on the page as its own row (its children `browser`, `browser_version`, `hostname` are): a record of web browser details. |
| 14 | `geo` | The geo RECORD contains information about the geographic location where the event was initiated. |
| 15 | `geo.region` | The region from which events were reported, based on IP address. |
| 16 | `app_info.id` | The package name or bundle ID of the app. |
| 17 | `app_info.install_source` | The store that installed the app. |
| 18 | `traffic_source.name` | Name of the marketing campaign that first acquired the user. This field is not populated in intraday tables. |
| 19 | `event_dimensions` | Not on the page. (In the export it's a record holding `hostname`.) |
| 20 | `ecommerce.purchase_revenue_in_usd` | Purchase revenue of this event, represented in USD with standard unit. Populated for purchase event only. |
| 21 | `ecommerce.refund_value` | The amount of refund in this event, represented in local currency with standard unit. Populated for refund event only. |
| 22 | `ecommerce.tax_value` | The tax value in this event, represented in local currency with standard unit. |
| 23 | `items.item_id` | The ID of the item. |
| 24 | `items.item_category` | The category of the item. |
| 25 | `items.item_category4` | The sub category of the item. |
| 26 | `items.quantity` | The quantity of the item. Quantity set to 1 if not specified. |
| 27 | `items.item_refund` | The refund value of this item, calculated as price * quantity. It is populated for refund events only, in local currency with standard unit. |
| 28 | `items.item_list_id` | The ID of the list in which the item was presented to the user. |
| 29 | `items.promotion_id` | The ID of a product promotion. |
| 30 | `event_date_dt` | Not a GA4 field: a DATE column we added in step 1 when copying the sample (`PARSE_DATE("%Y%m%d", event_date)`, see [poc/01-inspect/README.md](../../poc/01-inspect/README.md)), and the table's partition column. |

**How marks are given:** *right* = says the same thing as Google (or, for `event_date_dt`, what we built); *vague* = true but too general to tell this field from its neighbours (for example "a value"); *wrong* = contradicts Google (for example says USD where Google says local currency); *not described* = Studio wrote nothing for the field.
