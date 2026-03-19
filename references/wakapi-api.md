# Wakapi API (relevant to this skill)

[Wakapi](https://github.com/muety/wakapi) is a self-hosted coding-time stats service with a **native REST API** and **WakaTime-compatible** routes. This repo’s CLI only uses **read-only GET** endpoints that match WakaTime’s shape.

## Official resources

- Project: <https://github.com/muety/wakapi>
- Public instance (example): <https://wakapi.dev>

## Authentication

Same as this skill’s script: **HTTP Basic** with the **Base64-encoded API key** (same style as WakaTime docs):

```http
Authorization: Basic <base64(api_key)>
Accept: application/json
```

Server-side parsing of `Authorization` is implemented in Wakapi as `ExtractBearerAuth` (supports `Basic` / `Bearer` plus Base64 payload).

## Path prefixes (for reading stats)

Let the instance origin be `WAKAPI_URL` (no trailing `/`), e.g. `https://wakapi.dev` (aligned with `scripts/wakatime_query.py`).

| Use case | Prefix | Notes |
|----------|--------|--------|
| Most WakaTime-shaped read-only endpoints | `{origin}/api/compat/wakatime/v1` | `projects`, `stats`, `summaries`, `all-time-since`, and projects used by `health`, etc. |
| Today’s status bar | `{origin}/api/v1` | **Only** `…/users/current/statusbar/today` is fixed under `/api/v1` (Wakapi mounts both `/v1/...` and compat routes under `/api`). |

> Matches `scripts/wakatime_query.py`: the compat prefix is used when the origin’s hostname is **not** exactly `wakatime.com`; the **`status-bar`** subcommand always calls `{origin}/api/v1/users/current/statusbar/today`.

## Endpoints used by this CLI (GET)

| Subcommand | Path (after the prefix from the table above; `status-bar` is the exception) |
|------------|-----------------------------------------------------------------------------|
| `health` / `projects` | `/users/current/projects` |
| `all-time-since` | `/users/current/all_time_since_today` |
| `stats <range>` | `/users/current/stats/{range}`; optional query: `timeout`, `writes_only` |
| `summaries` | `/users/current/summaries`; query: `start`+`end` or `range`, plus `project`, `branches`, `timezone`, `timeout`, `writes_only`, etc. |
| `status-bar` | **Full URL** `{origin}/api/v1/users/current/statusbar/today` (no prefix-stacking rule) |

`{range}` must be URL-encoded (e.g. `last_7_days`, `all_time`).

## Summaries on Wakapi: `range` vs fixed dates

For **`summaries`** on **Wakapi** (compat API), the `range` query value is often a **lowercase token** passed through by this CLI as `--range` (e.g. `--range today`). Behaviour is implemented by your Wakapi version; the table below reflects **common** semantics on many deployments.

| Token | Typical window (through **today**, inclusive, unless noted) |
|-------|------------------------------------------------------------|
| `today` | Today only. |
| `yesterday` | **Yesterday through today** — *not* “yesterday only”. |
| `week` | This week’s **Monday** through today. |
| `month` | **1st of this month** through today. |
| `year` | **1 January** of this year through today. |
| `last_7_days` | The **previous 7 days plus today** → **8** calendar days in total. |

**Single calendar day only** (e.g. yesterday **without** including today): use an explicit date range with **`start` and `end` equal**:

```bash
export WAKAPI_URL="https://your-wakapi.example"
export WAKAPI_API_KEY="your-api-key"
python3 scripts/wakatime_query.py summaries --start 2026-03-18 --end 2026-03-18
```

Totals in the JSON (e.g. hours/minutes) come from the server; this script does not change aggregation rules.

**WakaTime cloud** uses different preset strings for `range` (e.g. `Last 7 Days`, `Yesterday`) — see [wakatime-api.md](wakatime-api.md) and [WakaTime Summaries](https://wakatime.com/developers#summaries).

## CLI vs HTTP timeouts (this repo’s script)

| Subcommand | HTTP client timeout |
|------------|---------------------|
| `health` / `projects` / `status-bar` / `all-time-since` | Subcommand **`--timeout`**; defaults **15** s (`health` only) and **60** s |
| `stats` / `summaries` | Fixed **60** s; **`--timeout`** on those commands (when present) is an **API query** parameter (keystroke timeout), not HTTP |

## Other APIs (not wrapped by this skill)

- **Heartbeats**, user settings, etc. use Wakapi’s **native** `/api/...` routes, not the compat prefix above; see Wakapi docs or `routes/api` in source.
- If deployed under a subpath (`base_path`), URLs must include that prefix; this script assumes **root** deployment.

## curl examples (replace key and host)

```bash
API_KEY='your-api-key'
B64=$(printf '%s' "$API_KEY" | base64 | tr -d '\n')
ORIGIN='https://wakapi.dev'

curl -sS -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  "$ORIGIN/api/compat/wakatime/v1/users/current/projects"

curl -sS -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  "$ORIGIN/api/v1/users/current/statusbar/today"
```
