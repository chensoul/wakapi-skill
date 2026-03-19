# WakaTime-compatible API — quick reference

Base URL variable: `WAKAPI_BASE_URL` (no trailing slash).  
Auth: `Authorization: Basic <base64(WAKAPI_API_KEY)>` per [WakaTime Developers](https://wakatime.com/developers) (HTTP Basic with API key).

OAuth Bearer is an alternative on WakaTime for token-based access; this skill assumes **API key + Basic** unless the server docs say otherwise.

## Endpoints (current user)

| Topic | GET path | Official anchor |
|-------|----------|-----------------|
| Summaries | `/api/v1/users/current/summaries` | [summaries](https://wakatime.com/developers#summaries) |
| Status bar (today) | `/api/v1/users/current/status_bar/today` | [status_bar](https://wakatime.com/developers#status_bar) |
| All time since today | `/api/v1/users/current/all_time_since_today` | [all_time_since_today](https://wakatime.com/developers#all_time_since_today) |
| Stats | `/api/v1/users/current/stats/{range}` | [stats](https://wakatime.com/developers#stats) |
| Projects | `/api/v1/users/current/projects` | [projects](https://wakatime.com/developers#projects) |

Full URL: `{WAKAPI_BASE_URL}` + path above.

## Summaries — query parameters

- **`start`** (Date) — required unless using `range`.
- **`end`** (Date) — required unless using `range`.
- **`range`** (String) — optional alternative to `start`/`end`. Examples from docs: `Today`, `Yesterday`, `Last 7 Days`, `Last 7 Days from Yesterday`, `Last 14 Days`, `Last 30 Days`, `This Week`, `Last Week`, `This Month`, `Last Month`.
- **`project`** (String) — optional filter.
- **`branches`** (String) — optional, comma-separated branch names.
- **`timeout`** (Integer) — optional keystroke timeout for joining heartbeats.
- **`writes_only`** (Boolean) — optional.
- **`timezone`** (String) — optional for interpreting `start`/`end`.

CLI ([`scripts/wakatime_query.py`](../scripts/wakatime_query.py)): `--project`, `--branches`, `--timezone`, `--timeout`, `--writes-only`, plus repeatable `--query KEY=VALUE` (named flags win on duplicate keys).

**Scope (WakaTime):** `read_summaries` (or narrower `read_summaries.*` scopes).

## Stats — path and query

- **Path:** `/stats/{range}` where `{range}` is one of:
  - Calendar: `YYYY` or `YYYY-MM`
  - Presets: `last_7_days`, `last_30_days`, `last_6_months`, `last_year`, `all_time`
- **Query (optional):** `timeout`, `writes_only`
- Response may include **`is_up_to_date`**. If false, stats might still be computing—retry later per product behavior.

**Scope (WakaTime):** `read_stats` (often bundled with summary-related scopes; see WakaTime OAuth scope list).

## Status bar / all_time_since_today / projects

- Typically **GET** with no required query parameters.
- Optional parameters, pagination, or filters—check the live documentation for your server version.

## Self-hosted Wakapi

Wakapi aims for WakaTime-compatible routes; always confirm **base URL**, **auth header format**, and **implemented routes** in your deployment’s documentation if calls fail or return empty data.

## Optional script

This skill’s [`scripts/wakatime_query.py`](../scripts/wakatime_query.py) (stdlib-only CLI) mirrors the five endpoints; use it if you prefer not to hand-craft `curl`.

- **`health`** — `GET /api/v1/users/current/projects` with a short timeout. **Healthy only if status is HTTP 200:** stdout `{"healthy": true}` and exit `0`; otherwise `{"healthy": false}` and exit `1`. Options: `--connect-timeout SEC` (default `15`).
