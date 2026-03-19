---
name: wakapi-wakatime-query
description: >-
  Read-only WakaTime / Wakapi coding stats (summaries, projects, today status, totals)
  via a small Python CLI. Requires WAKAPI_API_KEY: the script sends it as HTTP Basic
  authentication (Authorization: Basic base64(key)) to the configured API host.
  Optional WAKAPI_URL selects the host (omit for WakaTime cloud). Use when the
  user asks about WakaTime, Wakapi, coding time, or project/language breakdowns.
homepage: https://github.com/chensoul/wakapi-skill
repository: https://github.com/chensoul/wakapi-skill
metadata: {"openclaw": {"requires": {"env": ["WAKAPI_URL", "WAKAPI_API_KEY"]}, "primaryEnv": "WAKAPI_API_KEY"}}
---

# Wakapi / WakaTime API query

## When to use

The user wants **read-only** stats: time ranges, projects/languages, today’s status line, all-time total, or project list—from **WakaTime** or **Wakapi**.

## Requirements

| Category | Detail |
|----------|--------|
| **Runtime** | **Python 3** with **standard library only** (no pip/npm deps for [`scripts/wakatime_query.py`](scripts/wakatime_query.py)). |
| **Environment — required** | **`WAKAPI_API_KEY`** — API key from the user’s WakaTime or Wakapi account. |
| **Environment — optional** | **`WAKAPI_URL`** — Site origin (scheme + host; trailing `/` stripped). Omit for **WakaTime cloud** (`https://wakatime.com`). Set for **Wakapi** / self-hosted (e.g. `https://wakapi.dev`). Prefix logic: **`/api/v1`** for most endpoints only if hostname is **exactly** `wakatime.com`; otherwise **`/api/compat/wakatime/v1`**. **`status-bar`** always uses **`{origin}/api/v1/.../statusbar/today`**. |
| **Network** | Outbound **HTTPS** to the host above. |
| **Authentication** | **HTTP Basic**: `Authorization: Basic` + base64-encoded **API key only** (no username). Used only against the configured host; endpoints are **read-only** stats APIs. |
| **Registry / installers** | Frontmatter key **`metadata`** (JSON value): **`openclaw.requires.env`** = `["WAKAPI_URL", "WAKAPI_API_KEY"]`, **`primaryEnv`** = **`WAKAPI_API_KEY`**. Only the key is mandatory; host defaults when **`WAKAPI_URL`** is unset. |

No other environment variables are read by the CLI.

## Prerequisites

1. The user has (or can set) **`WAKAPI_API_KEY`** and, if needed, **`WAKAPI_URL`** — see **Requirements**.
2. Do **not** paste secrets into chat. If the key is missing, ask the user to configure the environment (shell, IDE, or agent env).

## Usage

Run **[`scripts/wakatime_query.py`](scripts/wakatime_query.py)** from the skill/repo root (Python 3, standard library only):

```bash
export WAKAPI_API_KEY="…"

# Optional — only if the user uses Wakapi (hosted or self‑hosted) instead of WakaTime:
# export WAKAPI_URL="https://wakapi.example.com"

python3 scripts/wakatime_query.py health
python3 scripts/wakatime_query.py projects
python3 scripts/wakatime_query.py status-bar
python3 scripts/wakatime_query.py all-time-since
python3 scripts/wakatime_query.py stats last_7_days
python3 scripts/wakatime_query.py summaries --start 2025-03-01 --end 2025-03-07
python3 scripts/wakatime_query.py summaries --range "Last 7 Days"
python3 scripts/wakatime_query.py summaries --range yesterday --timezone Asia/Shanghai
python3 scripts/wakatime_query.py summaries --start 2025-03-01 --end 2025-03-07 \
  --project myapp --branches main,develop --timezone Asia/Shanghai
```

- **`health`** — quick check; prints `{"healthy": true}` or `{"healthy": false}` and sets exit code accordingly.
- **`summaries --help`** — lists filters (`--project`, `--range`, `--timezone`, …).

## Interpreting output

Responses are JSON. Summarize totals and human-readable fields for the user; call out error messages from the payload if present.

For HTTP paths, auth, and endpoint tables, see **[references/wakapi-api.md](references/wakapi-api.md)** (Wakapi) and **[references/wakatime-api.md](references/wakatime-api.md)** (WakaTime).

## If something fails

Suggest checking the API key, which service they use (WakaTime vs Wakapi / self-hosted), and retrying later if the service might be down. For **summaries**, ensure a date range or preset range is provided (`--help`).

Only **`WAKAPI_API_KEY`** and optional **`WAKAPI_URL`** use the environment. For debug URLs, pass **`-d`** or **`--debug`** anywhere (e.g. `projects -d`). For slow HTTP, use **`--timeout`** on `health` (default 15s) / `projects` / `status-bar` / `all-time-since` (default 60s) — that flag is **HTTP socket** time only. On **`stats`** / **`summaries`**, **`--timeout`** (if used) is an **API query** parameter, not HTTP timeout; those commands use a built-in **60** s HTTP timeout.
