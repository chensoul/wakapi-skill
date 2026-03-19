# WakaTime cloud API (relevant to this skill)

[WakaTime](https://wakatime.com) exposes an HTTP API. This repo’s CLI only uses **read-only GET** endpoints under **v1** related to stats (not plugin heartbeats).

## Official documentation

- Developers: <https://wakatime.com/developers>
- API overview: <https://wakatime.com/api/>

## Base URL

Default site origin when `WAKAPI_URL` is unset or points at WakaTime (same as [wakatime.com](https://wakatime.com)):

```text
https://wakatime.com
```

That is the default **`WAKAPI_URL`** / origin. This CLI builds v1 stats URLs as **`{origin}/api/v1/...`** when the parsed hostname is **exactly** `wakatime.com` (see `_compat_api_prefix` in `scripts/wakatime_query.py`). The paths in the table below are shown from the site root (i.e. **`/api/v1/...`** after `https://wakatime.com`).

## Authentication

Per WakaTime: **HTTP Basic** with the **API key Base64-encoded** in `Authorization` (same as this skill with Wakapi):

```http
Authorization: Basic <base64(api_key)>
Accept: application/json
```

OAuth / `api_key` query and other methods exist in the docs; **this script only implements Basic**.

## Endpoints used by this CLI (GET)

| Subcommand | Path | Notes |
|------------|------|--------|
| `health` / `projects` | `/api/v1/users/current/projects` | `health` treats HTTP 200 as healthy |
| `status-bar` | Script calls: `https://wakatime.com/api/v1/users/current/statusbar/today` | Matches WakaTime (`statusbar`, no underscore) |
| `all-time-since` | `/api/v1/users/current/all_time_since_today` | |
| `stats <range>` | `/api/v1/users/current/stats/{range}` | `range` examples: `last_7_days`, `last_30_days`, `2025`, `2025-03`, `all_time`, etc.; optional query: `timeout`, `writes_only` |
| `summaries` | `/api/v1/users/current/summaries` | `start`+`end` (`YYYY-MM-DD`) or `range` (preset strings like `Last 7 Days`); optional: `project`, `branches`, `timezone`, `timeout` (keystroke timeout, not HTTP), `writes_only` |

Exact query parameters and response fields: official docs.

## CLI vs HTTP timeouts (this repo’s script)

| Subcommand | HTTP client timeout |
|------------|---------------------|
| `health` / `projects` / `status-bar` / `all-time-since` | Subcommand **`--timeout`** = HTTP socket; default **15** s (`health`) or **60** s |
| `stats` / `summaries` | HTTP **fixed 60** s; **`stats --timeout`** / **`summaries --timeout`** = **API** query parameter (keystroke timeout), not HTTP |

## curl examples (replace API key)

```bash
API_KEY='your-api-key'
B64=$(printf '%s' "$API_KEY" | base64 | tr -d '\n')

curl -sS -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  'https://wakatime.com/api/v1/users/current/projects'

curl -sS -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  'https://wakatime.com/api/v1/users/current/statusbar/today'
```

## Notes

- Features such as teams, leaderboards, OAuth, etc. are out of scope for this skill.
- If **`WAKAPI_URL`** uses a host **other than** `wakatime.com` (even another WakaTime-shaped service), this script uses the **compat** prefix for most endpoints; see [wakapi-api.md](wakapi-api.md).
