---
name: wakapi
description: >-
  Queries read-only coding-time stats from a Wakapi instance (projects, daily summaries,
  interval stats, status bar, all-time totals) using scripts/wakapi_query.py with Python 3
  stdlib only; Python >= 3.10. Requires WAKAPI_URL; WAKAPI_API_KEY for all subcommands
  except native GET /api/health. Use when the user mentions Wakapi, self-hosted coding stats, or
  WakaTime-compatible compat APIs under /api/compat/wakatime/v1.
homepage: https://github.com/chensoul/wakapi-skill
repository: https://github.com/chensoul/wakapi-skill
metadata: {"openclaw": {"requires": {"env": ["WAKAPI_URL", "WAKAPI_API_KEY"]}, "primaryEnv": "WAKAPI_API_KEY"}}
---

# Wakapi

## When to use

The user wants **read-only** data from their **Wakapi** server: project list, time ranges, per-day summaries, aggregate stats, today’s status line, or all-time total.

## Instructions

1. **Environment** — Ensure **`WAKAPI_URL`** is set (origin, no trailing `/`). For every subcommand **except** **`health`**, ensure **`WAKAPI_API_KEY`** is set. Do not ask the user to paste secrets into chat.
2. **Run the CLI** — From the **skill root** (directory containing this `SKILL.md`): `python3 scripts/wakapi_query.py …`. Use **`--help`** and **`summaries --help`** for flags.
3. **Choose the mode** — **`stats <range>`** uses a **named path segment** (Wakapi intervals only; **not** `YYYY` / `YYYY-MM` in the path). **`summaries`** uses **`--range`** *or* **`--start` + `--end`**; optional filters: **`--project`**, **`--branches`**, **`--timezone`**, **`--timeout`** (API keystroke), **`--writes-only`**. Details and preset tables: **[references/wakapi-api.md](references/wakapi-api.md)**.
4. **Respond to the user** — Output is JSON on stdout; summarize key numbers and labels. On failure, stderr often contains JSON with **`http_status`** / **`error`**.

## Requirements

| Item | Detail |
|------|--------|
| **Python** | **≥ 3.10** required (PEP 604 union types in annotations). |
| **`WAKAPI_URL`** | Required |
| **`WAKAPI_API_KEY`** | Required except for **`health`** |

## Examples

Minimal patterns; **full preset list, URL map, curl, and timeout rules** are in **[references/wakapi-api.md](references/wakapi-api.md)**.

```bash
export WAKAPI_URL="https://your-wakapi.example"
export WAKAPI_API_KEY="…"   # omit for health only

python3 scripts/wakapi_query.py health
python3 scripts/wakapi_query.py projects
python3 scripts/wakapi_query.py status-bar
python3 scripts/wakapi_query.py stats last_7_days
python3 scripts/wakapi_query.py summaries --range today
python3 scripts/wakapi_query.py summaries --start 2026-03-01 --end 2026-03-07 --timezone Asia/Shanghai
python3 scripts/wakapi_query.py summaries --range week --project myapp --branches main,develop
python3 scripts/wakapi_query.py -d projects    # debug: print request URLs to stderr
```

## If something fails

| Symptom | Check |
|---------|--------|
| `WAKAPI_URL is required` / connection errors | **`WAKAPI_URL`**, TLS, instance up |
| `WAKAPI_API_KEY is empty` | Key set for non-**`health`** calls |
| Bad **stats** range | Use **named** intervals (e.g. `last_7_days`, `year`); fixed calendar windows → **`summaries --start` / `--end`** |
| **Summaries** argparse error | **`--range`** xor **`--start`+`--end`**; not both |
| **`--timeout`** confusion | On **`health`** / **`projects`** / **`status-bar`** / **`all-time-since`** = HTTP socket. On **`stats`** / **`summaries`** = **API** keystroke param (HTTP stays 60s) — see reference |

---

**Reference (no duplicate in this file):** endpoints, **`stats` vs `summaries`**, **`--range` semantics**, **curl**, **CLI output streams** → **[references/wakapi-api.md](references/wakapi-api.md)**.
