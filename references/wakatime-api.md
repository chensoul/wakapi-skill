# WakaTime cloud API (relevant to this skill)

[WakaTime](https://wakatime.com) exposes an HTTP API. This repo’s CLI only uses **read-only GET** endpoints under **v1** related to stats (not plugin heartbeats).

## Official documentation

- Developers: <https://wakatime.com/developers>
- API overview: <https://wakatime.com/api/>

## Base URL

Default when `WAKAPI_URL` is unset or points at WakaTime:

```text
https://wakatime.com/api/v1
```

All paths below are appended to this prefix (no doubled leading `/`; the prefix already includes `/api/v1`).

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
| `health` / `projects` | `/users/current/projects` | `health` treats HTTP 200 as healthy |
| `status-bar` | Script calls: `https://wakatime.com/api/v1/users/current/statusbar/today` | Matches WakaTime (`statusbar`, no underscore) |
| `all-time-since` | `/users/current/all_time_since_today` | |
| `stats <range>` | `/users/current/stats/{range}` | `range` examples: `last_7_days`, `last_30_days`, `2025`, `2025-03`, `all_time`, etc.; optional query: `timeout`, `writes_only` |
| `summaries` | `/users/current/summaries` | `start`+`end` (`YYYY-MM-DD`) or `range` (preset strings like `Last 7 Days`); optional: `project`, `branches`, `timezone`, `timeout` (keystroke timeout, not HTTP), `writes_only` |

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
- Self-hosted compatible services (e.g. Wakapi) may use different path prefixes than plain WakaTime; see [wakapi-api.md](wakapi-api.md).
