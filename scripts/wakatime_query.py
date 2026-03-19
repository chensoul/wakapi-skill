#!/usr/bin/env python3
"""
WakaTime / Wakapi-compatible API helper (stdlib only).

Requires environment variables:
  WAKAPI_BASE_URL  — e.g. https://wakatime.com (no trailing slash, no /api/v1)
  WAKAPI_API_KEY   — secret API key

Examples:
  python3 scripts/wakatime_query.py projects
  python3 scripts/wakatime_query.py status-bar-today
  python3 scripts/wakatime_query.py all-time-since-today
  python3 scripts/wakatime_query.py stats last_7_days
  python3 scripts/wakatime_query.py summaries --start 2025-03-01 --end 2025-03-07
  python3 scripts/wakatime_query.py summaries --range "Last 7 Days" \\
    --project myapp --branches main,develop --timezone Asia/Shanghai
  python3 scripts/wakatime_query.py summaries --start 2025-03-01 --end 2025-03-07 \\
    --query project=myapp --query branches=main
  python3 scripts/wakatime_query.py health
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


def _normalize_base(url: str) -> str:
    u = url.strip().rstrip("/")
    if not u:
        raise SystemExit("WAKAPI_BASE_URL is empty")
    return u


def _auth_header(api_key: str) -> str:
    if not api_key:
        raise SystemExit("WAKAPI_API_KEY is empty")
    b64 = base64.b64encode(api_key.encode("utf-8")).decode("ascii")
    return f"Basic {b64}"


def _get_json(
    url: str,
    headers: dict[str, str],
    *,
    timeout: float = 60,
) -> tuple[int, Any]:
    req = urllib.request.Request(url, method="GET", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            code = resp.getcode()
            if not body:
                return code, None
            try:
                return code, json.loads(body)
            except json.JSONDecodeError as e:
                snippet = body[:200].replace("\n", " ")
                print(
                    f"Expected JSON in response body (HTTP {code}), parse error: {e}; "
                    f"body starts with: {snippet!r}",
                    file=sys.stderr,
                )
                raise SystemExit(1) from e
    except urllib.error.HTTPError as e:
        try:
            payload = e.read().decode("utf-8")
            data = json.loads(payload) if payload else None
        except json.JSONDecodeError:
            data = payload
        print(json.dumps({"http_status": e.code, "error": data}, indent=2), file=sys.stderr)
        # Always exit 1 on HTTP errors so shells see a stable failure code (avoid 401→145 mod 256).
        raise SystemExit(1) from e
    except urllib.error.URLError as e:
        print(str(e.reason if hasattr(e, "reason") else e), file=sys.stderr)
        raise SystemExit(2) from e


def cmd_health(base: str, hdr: dict[str, str], *, timeout: float = 15) -> None:
    """GET …/projects; healthy iff HTTP status is exactly 200. Minimal stdout JSON only."""
    path = "/api/v1/users/current/projects"
    url = f"{base}{path}"
    req = urllib.request.Request(url, method="GET", headers=hdr)
    code: int | None = None
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = resp.getcode()
            resp.read()  # drain body
    except urllib.error.HTTPError as e:
        try:
            e.read()
        except OSError:
            pass
        print(json.dumps({"healthy": False}))
        raise SystemExit(1) from e
    except urllib.error.URLError:
        print(json.dumps({"healthy": False}))
        raise SystemExit(1)

    healthy = code == 200
    print(json.dumps({"healthy": healthy}))
    raise SystemExit(0 if healthy else 1)


def cmd_projects(base: str, hdr: dict[str, str]) -> None:
    url = f"{base}/api/v1/users/current/projects"
    _code, data = _get_json(url, hdr)
    print(json.dumps(data, indent=2))


def cmd_status_bar_today(base: str, hdr: dict[str, str]) -> None:
    url = f"{base}/api/v1/users/current/status_bar/today"
    _code, data = _get_json(url, hdr)
    print(json.dumps(data, indent=2))


def cmd_all_time_since_today(base: str, hdr: dict[str, str]) -> None:
    url = f"{base}/api/v1/users/current/all_time_since_today"
    _code, data = _get_json(url, hdr)
    print(json.dumps(data, indent=2))


def cmd_stats(base: str, hdr: dict[str, str], args: argparse.Namespace) -> None:
    range_seg = urllib.parse.quote(args.stats_range, safe="")
    q: list[tuple[str, str]] = []
    if args.timeout is not None:
        q.append(("timeout", str(args.timeout)))
    if args.writes_only is not None:
        q.append(("writes_only", args.writes_only))
    qs = urllib.parse.urlencode(q) if q else ""
    url = f"{base}/api/v1/users/current/stats/{range_seg}"
    if qs:
        url = f"{url}?{qs}"
    _code, data = _get_json(url, hdr)
    print(json.dumps(data, indent=2))


def cmd_summaries(base: str, hdr: dict[str, str], args: argparse.Namespace) -> None:
    # Insertion-ordered map; explicit CLI flags override earlier --query keys.
    params: dict[str, str] = {}

    for raw in getattr(args, "extra_query", None) or []:
        if "=" not in raw:
            raise SystemExit(f"summaries: --query must be KEY=VALUE, got {raw!r}")
        key, _, value = raw.partition("=")
        key = key.strip()
        if not key:
            raise SystemExit(f"summaries: empty key in --query {raw!r}")
        params[key] = value

    if args.start and args.end:
        params["start"] = args.start
        params["end"] = args.end
    elif args.range_preset:
        params["range"] = args.range_preset
    else:
        raise SystemExit("summaries: provide --start and --end, or --range")

    if args.project:
        params["project"] = args.project
    if args.branches:
        params["branches"] = args.branches
    if args.timezone:
        params["timezone"] = args.timezone
    if args.timeout is not None:
        params["timeout"] = str(args.timeout)
    if args.writes_only is not None:
        params["writes_only"] = args.writes_only

    qs = urllib.parse.urlencode(params)
    url = f"{base}/api/v1/users/current/summaries"
    if qs:
        url = f"{url}?{qs}"
    _code, data = _get_json(url, hdr)
    print(json.dumps(data, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Query WakaTime-compatible /users/current APIs")
    sub = parser.add_subparsers(dest="command", required=True)

    p_health = sub.add_parser(
        "health",
        help="GET …/projects; stdout is {\"healthy\": true} iff HTTP 200, else {\"healthy\": false}",
    )
    p_health.add_argument(
        "--connect-timeout",
        type=float,
        default=15,
        metavar="SEC",
        dest="connect_timeout",
        help="HTTP timeout in seconds (default: 15)",
    )

    sub.add_parser("projects", help="GET /api/v1/users/current/projects")
    sub.add_parser("status-bar-today", help="GET .../status_bar/today")
    sub.add_parser("all-time-since-today", help="GET .../all_time_since_today")

    p_stats = sub.add_parser("stats", help="GET .../stats/{range}")
    p_stats.add_argument(
        "stats_range",
        metavar="range",
        help="e.g. last_7_days, 2025, 2025-03, all_time",
    )
    p_stats.add_argument("--timeout", type=int, default=None)
    p_stats.add_argument(
        "--writes-only",
        choices=("true", "false"),
        default=None,
        help="Query parameter writes_only",
    )

    p_sum = sub.add_parser(
        "summaries",
        help="GET .../summaries (optional filters: project, branches, timezone, …)",
    )
    p_sum.add_argument("--start", help="Start date (YYYY-MM-DD); use with --end")
    p_sum.add_argument("--end", help="End date (YYYY-MM-DD); use with --start")
    p_sum.add_argument(
        "--range",
        dest="range_preset",
        metavar="RANGE",
        help='Preset range, e.g. "Last 7 Days", Today (mutually exclusive with --start/--end)',
    )
    p_sum.add_argument(
        "--project",
        metavar="NAME",
        help="WakaTime query project: only time logged to this project",
    )
    p_sum.add_argument(
        "--branches",
        metavar="NAMES",
        help="WakaTime query branches: comma-separated branch names (e.g. main,develop)",
    )
    p_sum.add_argument(
        "--timezone",
        metavar="TZ",
        help="WakaTime query timezone: IANA zone for start/end (e.g. America/New_York)",
    )
    p_sum.add_argument(
        "--timeout",
        type=int,
        default=None,
        metavar="N",
        help="WakaTime query timeout: keystroke timeout (seconds) for joining heartbeats",
    )
    p_sum.add_argument(
        "--writes-only",
        choices=("true", "false"),
        default=None,
        help="WakaTime query writes_only",
    )
    p_sum.add_argument(
        "--query",
        dest="extra_query",
        action="append",
        default=None,
        metavar="KEY=VALUE",
        help="Extra query parameter (repeatable). --project/--branches/… override same key.",
    )

    args = parser.parse_args()

    base = _normalize_base(os.environ.get("WAKAPI_BASE_URL", ""))
    api_key = os.environ.get("WAKAPI_API_KEY", "")
    auth = os.environ.get("WAKAPI_BASIC_HEADER", "").strip()
    if auth:
        h = {"Authorization": auth, "Accept": "application/json"}
    else:
        h = {"Authorization": _auth_header(api_key), "Accept": "application/json"}

    if args.command == "summaries":
        has_dates = bool(args.start or args.end)
        if bool(args.start) ^ bool(args.end):
            parser.error("summaries: --start and --end must be used together")
        if has_dates and args.range_preset:
            parser.error("summaries: do not combine --range with --start/--end")
        if not has_dates and not args.range_preset:
            parser.error("summaries: need --start and --end, or --range")

    if args.command == "health":
        cmd_health(base, h, timeout=args.connect_timeout)
    elif args.command == "projects":
        cmd_projects(base, h)
    elif args.command == "status-bar-today":
        cmd_status_bar_today(base, h)
    elif args.command == "all-time-since-today":
        cmd_all_time_since_today(base, h)
    elif args.command == "stats":
        cmd_stats(base, h, args)
    elif args.command == "summaries":
        cmd_summaries(base, h, args)
    else:
        parser.error(f"unknown command {args.command!r}")


if __name__ == "__main__":
    main()
