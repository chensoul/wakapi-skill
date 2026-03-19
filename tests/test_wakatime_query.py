"""Unit tests for scripts/wakatime_query.py (no network)."""

from __future__ import annotations

import argparse
import base64
import importlib.util
import io
import json
import os
import sys
import unittest
import urllib.error
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "wakatime_query.py"
    spec = importlib.util.spec_from_file_location("wakatime_query", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["wakatime_query"] = mod
    spec.loader.exec_module(mod)
    return mod


wq = _load_module()


class _FakeUrlResponse:
    """Context manager returned by mocked urlopen for successful responses."""

    def __init__(self, code: int, body: bytes) -> None:
        self._code = code
        self._body = body

    def __enter__(self) -> _FakeUrlResponse:
        return self

    def __exit__(self, *args: object) -> bool:
        return False

    def read(self) -> bytes:
        return self._body

    def getcode(self) -> int:
        return self._code


def _http_error(code: int, body: bytes = b"{}") -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        "http://example.test/api",
        code,
        "status",
        {},
        io.BytesIO(body),
    )


class TestGetJsonMockUrlopen(unittest.TestCase):
    def tearDown(self) -> None:
        wq._RUNTIME["debug"] = False

    def test_200_parses_json(self) -> None:
        payload = {"data": [{"id": "p1"}]}
        body = json.dumps(payload).encode()
        with patch.object(wq.urllib.request, "urlopen", return_value=_FakeUrlResponse(200, body)):
            code, data = wq._get_json("http://example.test/x", {"Accept": "application/json"})
        self.assertEqual(code, 200)
        self.assertEqual(data, payload)

    def test_200_empty_body_returns_none(self) -> None:
        with patch.object(wq.urllib.request, "urlopen", return_value=_FakeUrlResponse(200, b"")):
            code, data = wq._get_json("http://example.test/x", {})
        self.assertEqual(code, 200)
        self.assertIsNone(data)

    def test_passes_timeout_to_urlopen(self) -> None:
        with patch.object(wq.urllib.request, "urlopen") as m_urlopen:
            m_urlopen.return_value = _FakeUrlResponse(200, b"{}")
            wq._get_json("http://example.test/y", {}, timeout=47.5)
        m_urlopen.assert_called_once()
        _req, kwargs = m_urlopen.call_args
        self.assertEqual(kwargs.get("timeout"), 47.5)

    def test_http_error_exits_1(self) -> None:
        err = _http_error(401, b'{"msg":"no"}')
        stderr = io.StringIO()
        try:
            with patch.object(wq.urllib.request, "urlopen", side_effect=err):
                with redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as cm:
                        wq._get_json("http://example.test/z", {})
            self.assertEqual(cm.exception.code, 1)
            err_payload = json.loads(stderr.getvalue())
            self.assertEqual(err_payload["http_status"], 401)
        finally:
            err.close()

    def test_urlerror_exits_2(self) -> None:
        stderr = io.StringIO()
        with patch.object(
            wq.urllib.request,
            "urlopen",
            side_effect=urllib.error.URLError("timed out"),
        ):
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as cm:
                    wq._get_json("http://example.test/offline", {})
        self.assertEqual(cm.exception.code, 2)

    def test_invalid_json_body_exits_1(self) -> None:
        stderr = io.StringIO()
        with patch.object(
            wq.urllib.request,
            "urlopen",
            return_value=_FakeUrlResponse(200, b"not-json"),
        ):
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as cm:
                    wq._get_json("http://example.test/bad", {})
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("parse error", stderr.getvalue())


class TestCmdHealthMockUrlopen(unittest.TestCase):
    def tearDown(self) -> None:
        wq._RUNTIME["debug"] = False

    def test_200_healthy_exit_0(self) -> None:
        out = io.StringIO()
        with patch.object(wq.urllib.request, "urlopen", return_value=_FakeUrlResponse(200, b"{}")):
            with redirect_stdout(out):
                with self.assertRaises(SystemExit) as cm:
                    wq.cmd_health("https://wakatime.com/api/v1", {}, timeout=9)
        self.assertEqual(cm.exception.code, 0)
        self.assertIn("true", out.getvalue())

    def test_http_error_unhealthy_exit_1(self) -> None:
        err = _http_error(503)
        out = io.StringIO()
        try:
            with patch.object(wq.urllib.request, "urlopen", side_effect=err):
                with redirect_stdout(out):
                    with self.assertRaises(SystemExit) as cm:
                        wq.cmd_health("https://wakatime.com/api/v1", {}, timeout=9)
            self.assertEqual(cm.exception.code, 1)
            self.assertIn("false", out.getvalue())
        finally:
            err.close()


class TestCmdProjectsMockUrlopen(unittest.TestCase):
    def tearDown(self) -> None:
        wq._RUNTIME["debug"] = False

    def test_prints_json(self) -> None:
        body = json.dumps({"data": []}).encode()
        out = io.StringIO()
        with patch.object(wq.urllib.request, "urlopen", return_value=_FakeUrlResponse(200, body)):
            with redirect_stdout(out):
                wq.cmd_projects("https://wakatime.com/api/v1", {}, http_timeout=None)
        printed = json.loads(out.getvalue())
        self.assertEqual(printed, {"data": []})


class TestMainMockUrlopen(unittest.TestCase):
    def tearDown(self) -> None:
        wq._RUNTIME["debug"] = False

    def test_projects_subcommand(self) -> None:
        env = {
            "WAKAPI_API_KEY": "secret-key",
            "WAKAPI_URL": "https://wakatime.com",
        }
        body = json.dumps({"data": []}).encode()
        out = io.StringIO()
        with patch.dict(os.environ, env, clear=False):
            with patch.object(wq.urllib.request, "urlopen", return_value=_FakeUrlResponse(200, body)):
                with patch.object(sys, "argv", ["wakatime_query.py", "projects"]):
                    with redirect_stdout(out):
                        wq.main()
        self.assertEqual(json.loads(out.getvalue()), {"data": []})

    def test_stats_builds_url_with_query(self) -> None:
        env = {
            "WAKAPI_API_KEY": "k",
            "WAKAPI_URL": "https://wakatime.com",
        }
        captured: dict[str, object] = {}

        def capture_urlopen(req, timeout=None, **_):
            captured["fullurl"] = req.full_url
            return _FakeUrlResponse(200, b"{}")

        out = io.StringIO()
        argv = [
            "wakatime_query.py",
            "stats",
            "last_7_days",
            "--timeout",
            "120",
            "--writes-only",
            "true",
        ]
        with patch.dict(os.environ, env, clear=False):
            with patch.object(wq.urllib.request, "urlopen", side_effect=capture_urlopen):
                with patch.object(sys, "argv", argv):
                    with redirect_stdout(out):
                        wq.main()
        url = captured["fullurl"]
        assert isinstance(url, str)
        self.assertIn("/users/current/stats/last_7_days", url)
        self.assertIn("timeout=120", url)
        self.assertIn("writes_only=true", url)

    def test_main_health_success(self) -> None:
        env = {"WAKAPI_API_KEY": "k", "WAKAPI_URL": "https://wakatime.com"}
        out = io.StringIO()
        with patch.dict(os.environ, env, clear=False):
            with patch.object(wq.urllib.request, "urlopen", return_value=_FakeUrlResponse(200, b"{}")):
                with patch.object(sys, "argv", ["wakatime_query.py", "health"]):
                    with redirect_stdout(out):
                        with self.assertRaises(SystemExit) as cm:
                            wq.main()
        self.assertEqual(cm.exception.code, 0)
        self.assertIn("true", out.getvalue())

    def test_main_status_bar_hits_statusbar_url(self) -> None:
        env = {"WAKAPI_API_KEY": "k", "WAKAPI_URL": "https://wakapi.dev"}
        captured: dict[str, object] = {}

        def cap(req, timeout=None, **_):
            captured["url"] = req.full_url
            return _FakeUrlResponse(200, b"{}")

        with patch.dict(os.environ, env, clear=False):
            with patch.object(wq.urllib.request, "urlopen", side_effect=cap):
                with patch.object(sys, "argv", ["wakatime_query.py", "status-bar"]):
                    with redirect_stdout(io.StringIO()):
                        wq.main()
        url = captured["url"]
        assert isinstance(url, str)
        self.assertTrue(url.endswith("/api/v1/users/current/statusbar/today"))

    def test_main_all_time_since(self) -> None:
        env = {"WAKAPI_API_KEY": "k", "WAKAPI_URL": "https://wakapi.dev"}
        captured: dict[str, object] = {}

        def cap(req, timeout=None, **_):
            captured["url"] = req.full_url
            return _FakeUrlResponse(200, b"{}")

        with patch.dict(os.environ, env, clear=False):
            with patch.object(wq.urllib.request, "urlopen", side_effect=cap):
                with patch.object(sys, "argv", ["wakatime_query.py", "all-time-since"]):
                    with redirect_stdout(io.StringIO()):
                        wq.main()
        url = captured["url"]
        assert isinstance(url, str)
        self.assertIn("/api/compat/wakatime/v1/users/current/all_time_since_today", url)

    def test_main_summaries_start_end(self) -> None:
        env = {"WAKAPI_API_KEY": "k", "WAKAPI_URL": "https://wakatime.com"}
        captured: dict[str, object] = {}

        def cap(req, timeout=None, **_):
            captured["url"] = req.full_url
            return _FakeUrlResponse(200, b"{}")

        argv = [
            "wakatime_query.py",
            "summaries",
            "--start",
            "2025-03-01",
            "--end",
            "2025-03-07",
            "--project",
            "x",
            "--timezone",
            "Asia/Shanghai",
            "--timeout",
            "42",
            "--writes-only",
            "false",
        ]
        with patch.dict(os.environ, env, clear=False):
            with patch.object(wq.urllib.request, "urlopen", side_effect=cap):
                with patch.object(sys, "argv", argv):
                    with redirect_stdout(io.StringIO()):
                        wq.main()
        url = captured["url"]
        assert isinstance(url, str)
        self.assertIn("/users/current/summaries?", url)
        self.assertIn("start=2025-03-01", url)
        self.assertIn("end=2025-03-07", url)
        self.assertIn("project=x", url)
        self.assertIn("timezone=", url)
        self.assertIn("timeout=42", url)
        self.assertIn("writes_only=false", url)

    def test_main_summaries_only_start_exits_2(self) -> None:
        env = {"WAKAPI_API_KEY": "k", "WAKAPI_URL": "https://wakatime.com"}
        stderr = io.StringIO()
        argv = ["wakatime_query.py", "summaries", "--start", "2025-01-01"]
        with patch.dict(os.environ, env, clear=False):
            with patch.object(sys, "argv", argv):
                with redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as cm:
                        wq.main()
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("summaries", stderr.getvalue())

    def test_main_summaries_range_with_start_exits_2(self) -> None:
        env = {"WAKAPI_API_KEY": "k", "WAKAPI_URL": "https://wakatime.com"}
        stderr = io.StringIO()
        argv = [
            "wakatime_query.py",
            "summaries",
            "--start",
            "2025-01-01",
            "--end",
            "2025-01-02",
            "--range",
            "Last 7 Days",
        ]
        with patch.dict(os.environ, env, clear=False):
            with patch.object(sys, "argv", argv):
                with redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as cm:
                        wq.main()
        self.assertEqual(cm.exception.code, 2)

    def test_main_summaries_neither_range_nor_dates_exits_2(self) -> None:
        env = {"WAKAPI_API_KEY": "k", "WAKAPI_URL": "https://wakatime.com"}
        stderr = io.StringIO()
        with patch.dict(os.environ, env, clear=False):
            with patch.object(sys, "argv", ["wakatime_query.py", "summaries"]):
                with redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as cm:
                        wq.main()
        self.assertEqual(cm.exception.code, 2)

    def test_main_debug_sets_runtime(self) -> None:
        env = {"WAKAPI_API_KEY": "k", "WAKAPI_URL": "https://wakatime.com"}
        stderr = io.StringIO()
        try:
            with patch.dict(os.environ, env, clear=False):
                with patch.object(wq.urllib.request, "urlopen", return_value=_FakeUrlResponse(200, b"{}")):
                    with patch.object(sys, "argv", ["wakatime_query.py", "-d", "projects"]):
                        with redirect_stdout(io.StringIO()):
                            with redirect_stderr(stderr):
                                wq.main()
            self.assertTrue(wq._RUNTIME["debug"])
            self.assertIn("wakatime_query: GET", stderr.getvalue())
        finally:
            wq._RUNTIME["debug"] = False

    def test_main_parse_args_unknown_command_branch(self) -> None:
        """Hit defensive `else` in main (impossible with stock argparse)."""
        env = {"WAKAPI_API_KEY": "k", "WAKAPI_URL": "https://wakatime.com"}
        orig = argparse.ArgumentParser.parse_args

        def hijack(self, args=None):
            ns = orig(self, args)
            ns.command = "__unknown__"
            return ns

        stderr = io.StringIO()
        with patch.dict(os.environ, env, clear=False):
            with patch.object(argparse.ArgumentParser, "parse_args", hijack):
                with patch.object(sys, "argv", ["wakatime_query.py", "health"]):
                    with redirect_stderr(stderr):
                        with self.assertRaises(SystemExit) as cm:
                            wq.main()
        self.assertEqual(cm.exception.code, 2)


class TestGetJsonMoreBranches(unittest.TestCase):
    def tearDown(self) -> None:
        wq._RUNTIME["debug"] = False

    def test_http_error_body_not_json_uses_raw_payload(self) -> None:
        err = _http_error(502, b"upstream failed")
        stderr = io.StringIO()
        try:
            with patch.object(wq.urllib.request, "urlopen", side_effect=err):
                with redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as cm:
                        wq._get_json("http://example.test/e", {})
            self.assertEqual(cm.exception.code, 1)
            payload = json.loads(stderr.getvalue())
            self.assertEqual(payload["http_status"], 502)
            self.assertEqual(payload["error"], "upstream failed")
        finally:
            err.close()

    def test_log_request_when_debug(self) -> None:
        wq._RUNTIME["debug"] = True
        stderr = io.StringIO()
        try:
            with patch.object(wq.urllib.request, "urlopen", return_value=_FakeUrlResponse(200, b"{}")):
                with redirect_stderr(stderr):
                    wq._get_json("http://example.test/dbg", {})
            self.assertIn("wakatime_query: GET http://example.test/dbg", stderr.getvalue())
        finally:
            wq._RUNTIME["debug"] = False


class TestCmdHealthMoreBranches(unittest.TestCase):
    def tearDown(self) -> None:
        wq._RUNTIME["debug"] = False

    def test_non_200_exit_1(self) -> None:
        out = io.StringIO()
        with patch.object(wq.urllib.request, "urlopen", return_value=_FakeUrlResponse(204, b"")):
            with redirect_stdout(out):
                with self.assertRaises(SystemExit) as cm:
                    wq.cmd_health("https://wakatime.com/api/v1", {}, timeout=5)
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("false", out.getvalue())

    def test_urlerror_exit_1(self) -> None:
        out = io.StringIO()
        with patch.object(
            wq.urllib.request,
            "urlopen",
            side_effect=urllib.error.URLError("network down"),
        ):
            with redirect_stdout(out):
                with self.assertRaises(SystemExit) as cm:
                    wq.cmd_health("https://wakatime.com/api/v1", {}, timeout=5)
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("false", out.getvalue())

    def test_http_error_read_oserror_ignored(self) -> None:
        class _Fp:
            def read(self, n=-1):
                raise OSError("simulated read failure")

            def close(self) -> None:
                pass

        err = urllib.error.HTTPError("http://t", 500, "err", {}, _Fp())
        out = io.StringIO()
        try:
            with patch.object(wq.urllib.request, "urlopen", side_effect=err):
                with redirect_stdout(out):
                    with self.assertRaises(SystemExit) as cm:
                        wq.cmd_health("https://wakatime.com/api/v1", {}, timeout=5)
            self.assertEqual(cm.exception.code, 1)
            self.assertIn("false", out.getvalue())
        finally:
            err.close()


class TestCmdStatusBarAndAllTime(unittest.TestCase):
    def tearDown(self) -> None:
        wq._RUNTIME["debug"] = False

    def test_status_bar_prints(self) -> None:
        with patch.dict(os.environ, {"WAKAPI_URL": "https://wakatime.com"}):
            body = json.dumps({"cached_at": "x", "data": {}}).encode()
            out = io.StringIO()
            with patch.object(wq.urllib.request, "urlopen", return_value=_FakeUrlResponse(200, body)):
                with redirect_stdout(out):
                    wq.cmd_status_bar_today({}, http_timeout=None)
            self.assertIn("cached_at", out.getvalue())

    def test_all_time_since_prints(self) -> None:
        body = json.dumps({"data": {"total_seconds": 1}}).encode()
        out = io.StringIO()
        with patch.object(wq.urllib.request, "urlopen", return_value=_FakeUrlResponse(200, body)):
            with redirect_stdout(out):
                wq.cmd_all_time_since_today("https://wakatime.com/api/v1", {}, http_timeout=None)
        self.assertEqual(json.loads(out.getvalue())["data"]["total_seconds"], 1)


class TestCmdSummaries(unittest.TestCase):
    def tearDown(self) -> None:
        wq._RUNTIME["debug"] = False

    def test_range_and_options_build_url(self) -> None:
        args = argparse.Namespace(
            start=None,
            end=None,
            range_preset="Last 7 Days",
            project="myapp",
            branches="main",
            timezone="UTC",
            timeout=10,
            writes_only="true",
        )
        captured: dict[str, object] = {}

        def cap(req, timeout=None, **_):
            captured["url"] = req.full_url
            return _FakeUrlResponse(200, b"{}")

        with patch.object(wq.urllib.request, "urlopen", side_effect=cap):
            with redirect_stdout(io.StringIO()):
                wq.cmd_summaries("https://wakatime.com/api/v1", {}, args)
        url = captured["url"]
        assert isinstance(url, str)
        self.assertIn("range=Last+7+Days", url.replace("%20", "+"))
        self.assertIn("project=myapp", url)

    def test_missing_range_exits(self) -> None:
        args = argparse.Namespace(
            start=None,
            end=None,
            range_preset=None,
            project=None,
            branches=None,
            timezone=None,
            timeout=None,
            writes_only=None,
        )
        with self.assertRaises(SystemExit) as cm:
            wq.cmd_summaries("https://wakatime.com/api/v1", {}, args)
        self.assertIn("summaries", str(cm.exception))


class TestNormalizeBase(unittest.TestCase):
    def test_empty_uses_default(self):
        self.assertEqual(wq._normalize_base(""), wq._DEFAULT_BASE)
        self.assertEqual(wq._normalize_base("   "), wq._DEFAULT_BASE)

    def test_strips_trailing_slash(self):
        self.assertEqual(wq._normalize_base("https://wakapi.dev/"), "https://wakapi.dev")

    def test_preserves_origin(self):
        self.assertEqual(wq._normalize_base("https://example.com"), "https://example.com")


class TestHostFromBase(unittest.TestCase):
    def test_wakatime(self):
        self.assertEqual(wq._host_from_base("https://wakatime.com"), "wakatime.com")

    def test_wakapi(self):
        self.assertEqual(wq._host_from_base("https://wakapi.dev"), "wakapi.dev")


class TestCompatApiPrefix(unittest.TestCase):
    def test_wakatime_cloud(self):
        self.assertEqual(wq._compat_api_prefix("https://wakatime.com"), "/api/v1")

    def test_other_host(self):
        self.assertEqual(
            wq._compat_api_prefix("https://wakapi.dev"),
            "/api/compat/wakatime/v1",
        )


class TestApiRootAndStatusbar(unittest.TestCase):
    def test_api_root_wakatime(self):
        with patch.dict(os.environ, {"WAKAPI_URL": "https://wakatime.com"}, clear=False):
            self.assertEqual(wq._api_root(), "https://wakatime.com/api/v1")

    def test_api_root_wakapi(self):
        with patch.dict(os.environ, {"WAKAPI_URL": "https://wakapi.dev"}, clear=False):
            self.assertEqual(
                wq._api_root(),
                "https://wakapi.dev/api/compat/wakatime/v1",
            )

    def test_api_root_empty_env_defaults_wakatime(self):
        with patch.dict(os.environ, {"WAKAPI_URL": ""}, clear=False):
            self.assertEqual(wq._api_root(), "https://wakatime.com/api/v1")

    def test_statusbar_always_api_v1(self):
        with patch.dict(os.environ, {"WAKAPI_URL": "https://wakapi.dev"}, clear=False):
            self.assertEqual(
                wq._statusbar_today_url(),
                "https://wakapi.dev/api/v1/users/current/statusbar/today",
            )
        with patch.dict(os.environ, {"WAKAPI_URL": "https://wakatime.com"}, clear=False):
            self.assertEqual(
                wq._statusbar_today_url(),
                "https://wakatime.com/api/v1/users/current/statusbar/today",
            )


class TestResolveHttpTimeout(unittest.TestCase):
    def test_cli_wins(self):
        self.assertEqual(
            wq._resolve_http_timeout(cli_sec=99.0, fallback_sec=15),
            99.0,
        )

    def test_fallback(self):
        self.assertEqual(
            wq._resolve_http_timeout(cli_sec=None, fallback_sec=15),
            15,
        )


class TestStripDebugArgv(unittest.TestCase):
    def test_removes_flags(self):
        dbg, rest = wq._strip_debug_argv(["projects", "-d"])
        self.assertTrue(dbg)
        self.assertEqual(rest, ["projects"])

    def test_multiple_debug(self):
        dbg, rest = wq._strip_debug_argv(["-d", "health", "--debug"])
        self.assertTrue(dbg)
        self.assertEqual(rest, ["health"])

    def test_no_debug(self):
        dbg, rest = wq._strip_debug_argv(["stats", "last_7_days"])
        self.assertFalse(dbg)
        self.assertEqual(rest, ["stats", "last_7_days"])


class TestAuthBasic(unittest.TestCase):
    def test_encodes_utf8(self):
        key = "waka_test"
        expected = "Basic " + base64.b64encode(key.encode("utf-8")).decode("ascii")
        self.assertEqual(wq._auth_basic_value(key), expected)

    def test_empty_exits(self):
        with self.assertRaises(SystemExit) as ctx:
            wq._auth_basic_value("")
        self.assertEqual(str(ctx.exception), "WAKAPI_API_KEY is empty")


class TestRequestHeaders(unittest.TestCase):
    def test_requires_key(self):
        with patch.dict(os.environ, {"WAKAPI_API_KEY": ""}):
            with self.assertRaises(SystemExit) as ctx:
                wq._request_headers()
            self.assertEqual(str(ctx.exception), "WAKAPI_API_KEY is empty")

    def test_shape(self):
        with patch.dict(os.environ, {"WAKAPI_API_KEY": "abc"}, clear=False):
            h = wq._request_headers()
            self.assertEqual(h["Accept"], "application/json")
            self.assertTrue(h["Authorization"].startswith("Basic "))
            self.assertEqual(
                h["Authorization"],
                wq._auth_basic_value("abc"),
            )


class TestRuntimeDebug(unittest.TestCase):
    def tearDown(self):
        wq._RUNTIME["debug"] = False

    def test_debug_enabled_reads_runtime(self):
        wq._RUNTIME["debug"] = True
        self.assertTrue(wq._debug_enabled())
        wq._RUNTIME["debug"] = False
        self.assertFalse(wq._debug_enabled())


if __name__ == "__main__":
    unittest.main()
