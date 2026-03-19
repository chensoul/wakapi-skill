# Wakapi — API & CLI reference

**Audience:** exact URLs, HTTP auth, interval presets, full CLI examples, curl, timeouts, and stdout/stderr behavior.

**Agent-oriented summary:** **[SKILL.md](../SKILL.md)** (when to use, minimal examples, troubleshooting cues). This file does not repeat that workflow.

---

## What the CLI calls

[Wakapi](https://github.com/muety/wakapi) provides a **native** REST API and a **compat** layer at **`/api/compat/wakatime/v1`**. [`scripts/wakapi_query.py`](../scripts/wakapi_query.py) uses **read-only GET** plus **`GET /api/health`**. **Python ≥ 3.10**; **CI** and **`.python-version`** use **3.10** (same as minimum).

**Official resources**

- Repo: <https://github.com/muety/wakapi>
- Example instance: <https://wakapi.dev>
- Health handler: [`routes/api/health.go`](https://github.com/muety/wakapi/blob/master/routes/api/health.go)

## Environment

| Variable | Required | Notes |
|----------|----------|--------|
| **`WAKAPI_URL`** | Yes | Origin, **no** trailing `/` |
| **`WAKAPI_API_KEY`** | Yes* | *Skipped for **`health`** only |

## Authentication

Compat and **`/api/v1/.../statusbar/today`**:

```http
Authorization: Basic <base64(api_key)>
Accept: application/json
```

**`GET /api/health`** — no API key by default. This CLI sends **`Content-Type: application/json`** so Wakapi returns JSON (`{"app":1,"db":1}`).

## Path prefixes

| Purpose | Path |
|---------|------|
| Health | **`{ORIGIN}/api/health`** |
| Compat user stats | **`{ORIGIN}/api/compat/wakatime/v1/users/current/...`** |
| Status bar only | **`{ORIGIN}/api/v1/users/current/statusbar/today`** |

`ORIGIN` = **`WAKAPI_URL`**.

## Endpoints ↔ subcommands

| Subcommand | URL |
|------------|-----|
| `health` | `{ORIGIN}/api/health` |
| `projects` | `…/compat/wakatime/v1/users/current/projects` |
| `all-time-since` | `…/compat/.../all_time_since_today` |
| `stats <range>` | `…/compat/.../stats/{range}` |
| `summaries` | `…/compat/.../summaries` |
| `status-bar` | `{ORIGIN}/api/v1/users/current/statusbar/today` |

### `stats` vs `summaries`

| Aspect | **`stats <range>`** | **`summaries`** |
|--------|---------------------|-----------------|
| **Where** | `{range}` is a **path** segment | Query **`range=`** or **`start`+`end`** |
| **Wakapi values** | **Named intervals** from [`models/interval.go`](https://github.com/muety/wakapi/blob/master/models/interval.go) — e.g. `today`, `last_7_days`, `year` | Same **aliases** as presets, **or** fixed **`YYYY-MM-DD`** |
| **Stats path limits** | **`YYYY`** / **`YYYY-MM`** are **not** valid path segments — use **`summaries --start` / `--end`** for calendar buckets | — |

### CLI flags (`stats` / `summaries`)

| Subcommand | `--timeout` | `--writes-only` |
|------------|-------------|-----------------|
| **`stats`** | Query **`timeout`** (keystroke, API); HTTP client **60s** | Query **`writes_only`** |
| **`summaries`** | Same | Same |

| **`summaries` only** | Maps to query |
|----------------------|---------------|
| `--range` | `range` (mutually exclusive with `--start`/`--end`) |
| `--start` / `--end` | `start`, `end` |
| `--timezone` | `timezone` |
| `--project` | `project` |
| `--branches` | `branches` (comma-separated) |

## `--range` preset semantics (summaries & interval model)

Resolved via Wakapi’s interval helpers ([`models/interval.go`](https://github.com/muety/wakapi/blob/master/models/interval.go), [`helpers/interval.go`](https://github.com/muety/wakapi/blob/master/helpers/interval.go)). Many strings are aliases for the same window.

| Example `--range` | Meaning |
|-------------------|--------|
| `today` | Start of today → now |
| `yesterday`, `day` | Previous calendar day |
| `week` | This week (user week start) → now |
| `month` | This calendar month → now |
| `year` | This calendar year → now |
| `last_7_days`, `7_days`, `Last 7 Days` | Rolling 7 days |
| `last_14_days`, `14_days`, … | Rolling 14 days |
| `last_30_days`, `30_days`, … | Rolling 30 days |
| `last_week`, `Last Week` | Previous full week |
| `last_month`, `Last Month` | Previous calendar month |
| `last_year`, `12_months`, `last_12_months` | **Rolling 12 months** — not “calendar year 2024” |
| `all_time`, `any`, `All Time` | Epoch → now; **large / slow** |

More: `Last 7 Days from Yesterday`, `This Week`, `6_months` / `last_6_months`, etc.; see source and [`summaries` route](https://github.com/muety/wakapi/blob/master/routes/compat/wakatime/v1/summaries.go).

**Fixed dates:** `--start` and `--end` together (`YYYY-MM-DD`). One day → **same date twice**.

## CLI output (`wakapi_query.py`)

| Outcome | Stream |
|---------|--------|
| Success | stdout: JSON (indented for most commands). **`health`**: compact `{"healthy":…}`; may include **`detail`** if unhealthy |
| HTTP error | stderr: JSON `http_status` / `error`; exit **1** |
| Network / bad URL | stderr: text; exit **2** |

## CLI vs HTTP timeouts

| Subcommand | Socket timeout |
|------------|----------------|
| `health` / `projects` / `status-bar` / `all-time-since` | Subcommand **`--timeout`**; defaults **15s** (`health`), **60s** else |
| `stats` / `summaries` | HTTP **60s**; CLI **`--timeout`** = **API** keystroke parameter |

## Full CLI examples

```bash
export WAKAPI_URL="https://your-wakapi.example"
export WAKAPI_API_KEY="…"

python3 scripts/wakapi_query.py --help
python3 scripts/wakapi_query.py summaries --help

python3 scripts/wakapi_query.py health
python3 scripts/wakapi_query.py health --timeout 30

python3 scripts/wakapi_query.py projects
python3 scripts/wakapi_query.py projects --timeout 120
python3 scripts/wakapi_query.py status-bar
python3 scripts/wakapi_query.py all-time-since

python3 scripts/wakapi_query.py stats today
python3 scripts/wakapi_query.py stats yesterday
python3 scripts/wakapi_query.py stats week
python3 scripts/wakapi_query.py stats month
python3 scripts/wakapi_query.py stats year
python3 scripts/wakapi_query.py stats last_7_days
python3 scripts/wakapi_query.py stats last_30_days
python3 scripts/wakapi_query.py stats last_6_months
python3 scripts/wakapi_query.py stats last_year
python3 scripts/wakapi_query.py stats all_time
python3 scripts/wakapi_query.py stats last_7_days --timeout 300

python3 scripts/wakapi_query.py summaries --range today
python3 scripts/wakapi_query.py summaries --range yesterday
python3 scripts/wakapi_query.py summaries --range week
python3 scripts/wakapi_query.py summaries --range month
python3 scripts/wakapi_query.py summaries --range year
python3 scripts/wakapi_query.py summaries --range last_7_days
python3 scripts/wakapi_query.py summaries --range "Last 7 Days"
python3 scripts/wakapi_query.py summaries --range "Last 7 Days from Yesterday"
python3 scripts/wakapi_query.py summaries --range last_14_days
python3 scripts/wakapi_query.py summaries --range last_30_days
python3 scripts/wakapi_query.py summaries --range last_week
python3 scripts/wakapi_query.py summaries --range last_month
python3 scripts/wakapi_query.py summaries --range last_year
python3 scripts/wakapi_query.py summaries --range all_time

python3 scripts/wakapi_query.py summaries --range last_7_days --timezone Asia/Shanghai
python3 scripts/wakapi_query.py summaries --range week --project myapp --branches main,develop
python3 scripts/wakapi_query.py summaries --range today --writes-only true --timeout 300

python3 scripts/wakapi_query.py summaries --start 2026-03-01 --end 2026-03-07
python3 scripts/wakapi_query.py summaries --start 2026-03-01 --end 2026-03-07 --timezone America/New_York
python3 scripts/wakapi_query.py summaries --start 2026-03-01 --end 2026-03-07 --branches main,develop
python3 scripts/wakapi_query.py summaries --start 2026-03-18 --end 2026-03-18 \
  --project myapp --branches main,develop --timezone Asia/Shanghai --writes-only false

python3 scripts/wakapi_query.py -d projects
```

## curl examples

```bash
API_KEY='your-api-key'
B64=$(printf '%s' "$API_KEY" | base64 | tr -d '\n')
ORIGIN='https://wakapi.dev'
COMPAT="$ORIGIN/api/compat/wakatime/v1/users/current"

curl -sS -H 'Content-Type: application/json' -H 'Accept: application/json' \
  "$ORIGIN/api/health"
curl -sS "$ORIGIN/api/health"

curl -sS -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  "$COMPAT/projects"
curl -sS -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  "$COMPAT/all_time_since_today"
curl -sS -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  "$COMPAT/stats/last_7_days"

curl -sS -G -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  --data-urlencode "timeout=120" \
  --data-urlencode "writes_only=true" \
  "$COMPAT/stats/last_7_days"

curl -sS -G -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  --data-urlencode "range=today" \
  "$COMPAT/summaries"
curl -sS -G -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  --data-urlencode "range=last_7_days" \
  --data-urlencode "timezone=Asia/Shanghai" \
  "$COMPAT/summaries"

curl -sS -G -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  --data-urlencode "range=week" \
  --data-urlencode "project=myapp" \
  --data-urlencode "branches=main,develop" \
  --data-urlencode "timeout=300" \
  --data-urlencode "writes_only=true" \
  "$COMPAT/summaries"

curl -sS -G -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  --data-urlencode "start=2026-03-01" \
  --data-urlencode "end=2026-03-07" \
  "$COMPAT/summaries"

curl -sS -G -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  --data-urlencode "start=2026-03-18" \
  --data-urlencode "end=2026-03-18" \
  --data-urlencode "project=myapp" \
  --data-urlencode "branches=main,develop" \
  --data-urlencode "timezone=Asia/Shanghai" \
  "$COMPAT/summaries"

curl -sS -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  "$ORIGIN/api/v1/users/current/statusbar/today"
```

## Out of scope

- Other native **`/api/...`** routes (heartbeats, settings, …) — see Wakapi `routes/api`.
- **`base_path`** deployments: URLs must include the prefix; this script assumes **root**.
