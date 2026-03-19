---
name: wakapi-wakatime-query
description: >-
  Queries WakaTime-compatible coding activity APIs (WakaTime cloud or self-hosted Wakapi)
  for summaries, daily status bar, all-time totals, range stats, and projects. Uses
  WAKAPI_BASE_URL and WAKAPI_API_KEY. Portable agent skill for Cursor, Claude Code,
  OpenClaw, Codex, and other tools that load markdown skills. Use when the user asks
  about WakaTime, Wakapi, coding time, programming statistics, summaries, stats,
  projects, or status bar data.
---

# Wakapi / WakaTime API query

## Portable skill format

This directory is a **generic agent skill**: `SKILL.md` uses YAML frontmatter plus Markdown instructions. Any product that discovers skills from such files (e.g. **Cursor**, **Claude Code**, **OpenClaw**, **Codex**, or custom runners) can use it—installation path depends on that product (see the repo [README.md](README.md)).

## When to use

Apply this skill when the user wants **read-only** data from their account: time ranges, languages/projects breakdown, today’s status bar text, all-time time since today, or project lists—via **WakaTime** or a **WakaTime-compatible** server (e.g. **Wakapi**).

## Prerequisites

1. Environment variables must be set in the execution environment (shell, CI, user profile, or whatever terminal the agent uses):
   - `WAKAPI_BASE_URL` — API origin **without** `/api/v1` (e.g. `https://wakatime.com` or `https://wakapi.example.com`). **No trailing slash**; if the user set one, strip it before building URLs (avoid `//api/v1/...`).
   - `WAKAPI_API_KEY` — secret API key (WakaTime “API Key” from account settings, or the equivalent token your Wakapi instance documents).
   - *(Optional)* `WAKAPI_BASIC_HEADER` — full `Authorization` value (e.g. `Basic …` or, if your server requires it, a preformatted header). When set, **`curl`/scripts should use this instead of building Basic auth from `WAKAPI_API_KEY`**.

2. **Never** paste the full API key into chat logs. If variables are missing, ask the user to set them and retry.

A local **`.env` file is not auto-loaded** by this skill’s script; the user must `export` variables, `source` `.env` in the shell, or rely on their tool/CI to inject env (see [README.md](README.md)).

## Authentication

WakaTime documents **HTTP Basic** using only the API key:

- Compute `CRED_B64` as Base64 encoding of the raw API key string (no `username:password` concatenation unless your server docs say otherwise).
- Send header: `Authorization: Basic <CRED_B64>`

OAuth **Bearer** tokens are supported by WakaTime for some flows; this skill standardizes on **API key + Basic** unless the user explicitly says their server requires something else.

## Building URLs

All paths below are appended to `WAKAPI_BASE_URL`:

| Capability | Method | Path |
|------------|--------|------|
| Summaries | GET | `/api/v1/users/current/summaries` |
| Status bar (today) | GET | `/api/v1/users/current/status_bar/today` |
| All time since today | GET | `/api/v1/users/current/all_time_since_today` |
| Stats | GET | `/api/v1/users/current/stats/{range}` |
| Projects | GET | `/api/v1/users/current/projects` |

Use **`current`** as shown so the key always refers to the authenticated user.

### Query / path parameters

- **Summaries** — Either:
  - **`start`** and **`end`** (dates, format per API—typically `YYYY-MM-DD`), **or**
  - **`range`** as a single query alternative (e.g. `Today`, `Last 7 Days`, `This Week`, … per [Summaries](https://wakatime.com/developers#summaries)).
  - Optional: `project`, `branches`, `timeout`, `writes_only`, `timezone`.
- **Stats** — Path segment **`range`**: `YYYY`, `YYYY-MM`, or `last_7_days`, `last_30_days`, `last_6_months`, `last_year`, `all_time` (see [Stats](https://wakatime.com/developers#stats)). Optional query: `timeout`, `writes_only`. If `is_up_to_date` is false, the payload may still be stale—retry once after a short delay per vendor behavior.
- **status_bar/today**, **all_time_since_today**, **projects** — Usually no required params; optional filters depend on server (check official docs if a call fails).

Official reference: [WakaTime Developers](https://wakatime.com/developers).

## How to execute requests

Prefer **`curl`** in a terminal the user (or agent) can run with their env already loaded.

### Portable header construction

Avoid embedding the secret in the command history as plain text when possible; reading from the env is acceptable on the user’s machine.

**Option A — inline (shell):**

```bash
AUTH=$(printf '%s' "$WAKAPI_API_KEY" | base64 | tr -d '\n')
curl -sS -H "Authorization: Basic ${AUTH}" \
  "${WAKAPI_BASE_URL}/api/v1/users/current/projects"
```

**Option B — GNU coreutils note:** `base64 -w0` can replace `tr -d '\n'` on Linux if wrapping occurs.

**Option C — user supplies pre-encoded header (advanced):** if they export `WAKAPI_BASIC_HEADER` as the full `Basic …` value, use `-H "Authorization: ${WAKAPI_BASIC_HEADER}"` (not part of the default two-variable contract).

### Examples (adjust query strings as needed)

```bash
# Projects
curl -sS -H "Authorization: Basic $(printf '%s' "$WAKAPI_API_KEY" | base64 | tr -d '\n')" \
  "${WAKAPI_BASE_URL}/api/v1/users/current/projects"

# All time since today
curl -sS -H "Authorization: Basic $(printf '%s' "$WAKAPI_API_KEY" | base64 | tr -d '\n')" \
  "${WAKAPI_BASE_URL}/api/v1/users/current/all_time_since_today"

# Status bar today
curl -sS -H "Authorization: Basic $(printf '%s' "$WAKAPI_API_KEY" | base64 | tr -d '\n')" \
  "${WAKAPI_BASE_URL}/api/v1/users/current/status_bar/today"

# Stats (example range)
curl -sS -H "Authorization: Basic $(printf '%s' "$WAKAPI_API_KEY" | base64 | tr -d '\n')" \
  "${WAKAPI_BASE_URL}/api/v1/users/current/stats/last_7_days"

# Summaries (date range)
curl -sS -G -H "Authorization: Basic $(printf '%s' "$WAKAPI_API_KEY" | base64 | tr -d '\n')" \
  --data-urlencode "start=2025-03-01" \
  --data-urlencode "end=2025-03-07" \
  "${WAKAPI_BASE_URL}/api/v1/users/current/summaries"

# Summaries with optional filters (project, branches, timezone — URL-encode values as needed)
curl -sS -G -H "Authorization: Basic $(printf '%s' "$WAKAPI_API_KEY" | base64 | tr -d '\n')" \
  --data-urlencode "start=2025-03-01" \
  --data-urlencode "end=2025-03-07" \
  --data-urlencode "project=myapp" \
  --data-urlencode "branches=main,develop" \
  --data-urlencode "timezone=Asia/Shanghai" \
  "${WAKAPI_BASE_URL}/api/v1/users/current/summaries"
```

Use `-G` with `--data-urlencode` so query parameters are sent on a GET request.

### Optional: Python helper (stdlib only)

This repo includes [`scripts/wakatime_query.py`](scripts/wakatime_query.py): same env vars, **no third-party dependencies**, prints pretty JSON to stdout.

```bash
python3 scripts/wakatime_query.py health
python3 scripts/wakatime_query.py projects
python3 scripts/wakatime_query.py status-bar-today
python3 scripts/wakatime_query.py all-time-since-today
python3 scripts/wakatime_query.py stats last_7_days
python3 scripts/wakatime_query.py summaries --start 2025-03-01 --end 2025-03-07
python3 scripts/wakatime_query.py summaries --range "Last 7 Days"
# Optional summaries filters (see WakaTime docs): project, branches, timezone, timeout, writes_only
python3 scripts/wakatime_query.py summaries --start 2025-03-01 --end 2025-03-07 \
  --project myapp --branches main,develop --timezone Asia/Shanghai
# Or pass any extra query key=value (named flags override --query on duplicate keys)
python3 scripts/wakatime_query.py summaries --range "Today" --query project=myapp --query branches=main
```

`health` calls `GET …/projects` with a short HTTP timeout (default 15s, override with `--connect-timeout`). **Only HTTP `200` counts as healthy:** stdout is exactly `{"healthy": true}` and exit code `0`; any other outcome is `{"healthy": false}` with exit code `1` (no extra fields or error bodies).

Run `python3 scripts/wakatime_query.py summaries --help` for all options. Advanced: if `WAKAPI_BASIC_HEADER` is set to a full `Basic …` value, the script uses it instead of deriving Basic auth from `WAKAPI_API_KEY`.

## Interpreting responses

- Expect JSON with a top-level `data` object or array for many endpoints (shape matches WakaTime docs).
- Summarize for the user: totals, human-readable fields (`text`, `digital`, `human_readable_*`), and top projects/languages when relevant.
- If the JSON contains errors or messages, surface them clearly.

## Error handling

| HTTP | Likely cause |
|------|----------------|
| 401 / 403 | Invalid or revoked API key; wrong auth scheme for this server. |
| 404 | Wrong `WAKAPI_BASE_URL`, typo in path, or endpoint not implemented on a custom server. |
| 400 | Missing required query params (e.g. summaries without `start`/`end` or `range`). |
| 5xx | Upstream outage; retry with backoff. |

If the user uses **self-hosted Wakapi**, behavior may differ slightly from WakaTime—defer to that instance’s documentation for auth quirks or missing endpoints.

## Further detail

See [references/reference.md](references/reference.md) for a compact endpoint and parameter cheat sheet.
