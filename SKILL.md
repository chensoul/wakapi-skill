---
name: wakapi-wakatime-query
description: >-
  Fetches coding time stats (summaries, today status, totals, range stats, projects)
  from the user’s WakaTime or Wakapi account via a small Python CLI. Needs
  WAKAPI_API_KEY; optional WAKAPI_BASE_URL (default WakaTime cloud). Use when the user
  asks about WakaTime, Wakapi, coding time, or project/language breakdowns.
---

# Wakapi / WakaTime API query

## Portable skill format

This directory is a **generic agent skill** (`SKILL.md` + YAML frontmatter). Install location depends on the product (see [README.md](README.md)).

## When to use

The user wants **read-only** stats: time ranges, projects/languages, today’s status line, all-time total, or project list—from **WakaTime** or **Wakapi**.

## Prerequisites

1. **`WAKAPI_API_KEY`** — required (from the user’s WakaTime or Wakapi account settings).
2. **`WAKAPI_BASE_URL`** — optional. Omit it to use **WakaTime cloud** (`https://wakatime.com`). Set it to a **Wakapi** instance (e.g. `https://wakapi.dev` or self-hosted) when the user does not use WakaTime.
3. Do **not** paste secrets into chat. If the key is missing, ask the user to configure the environment.

## How to run

Run **[`scripts/wakatime_query.py`](scripts/wakatime_query.py)** from the skill/repo root (Python 3, standard library only):

```bash
export WAKAPI_API_KEY="…"

# Optional — only if the user uses Wakapi (hosted or self‑hosted) instead of WakaTime:
# export WAKAPI_BASE_URL="https://wakapi.example.com"

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

Only **`WAKAPI_API_KEY`** and optional **`WAKAPI_BASE_URL`** use the environment. For debug URLs, pass **`-d`** or **`--debug`** anywhere (e.g. `projects -d`). For slow HTTP, use **`--timeout`** on `health` (default 15s) / `projects` / `status-bar` / `all-time-since` (default 60s) — that flag is **HTTP socket** time only. On **`stats`** / **`summaries`**, **`--timeout`** (if used) is an **API query** parameter, not HTTP timeout; those commands use a built-in **60** s HTTP timeout.
