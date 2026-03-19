# wakapi-skill

[![ClawHub](https://img.shields.io/badge/ClawHub-wakapi--skill-blue)](https://clawhub.ai/skills/wakapi-skill)
[![ClawHub version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fclawhub.ai%2Fapi%2Fv1%2Fskills%2Fwakapi-skill&query=%24.skill.tags.latest&label=clawhub&prefix=v&color=blue)](https://clawhub.ai/skills/wakapi-skill)
[![ClawHub downloads](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fclawhub.ai%2Fapi%2Fv1%2Fskills%2Fwakapi-skill&query=%24.skill.stats.downloads&label=clawhub%20downloads&color=blue)](https://clawhub.ai/skills/wakapi-skill)
[![GitHub stars](https://img.shields.io/github/stars/chensoul/wakapi-skill?style=flat&logo=github)](https://github.com/chensoul/wakapi-skill)
[![License](https://img.shields.io/github/license/chensoul/wakapi-skill)](./LICENSE)
[![Publish to ClawHub](https://github.com/chensoul/wakapi-skill/actions/workflows/clawhub-publish.yml/badge.svg)](https://github.com/chensoul/wakapi-skill/actions/workflows/clawhub-publish.yml)

Portable **agent skill** to query **WakaTime** or **Wakapi** coding stats via a small Python CLI. 

## Layout

```
wakapi-skill/
├── SKILL.md
├── README.md
├── LICENSE
├── references/
│   ├── wakapi-api.md
│   └── wakatime-api.md
├── scripts/
│   └── wakatime_query.py
└── tests/
    └── test_wakatime_query.py
```

Symlink or copy the folder into your product’s skills directory so `SKILL.md` is discovered.

## Configuration

| Variable | Required | Purpose |
|----------|----------|---------|
| `WAKAPI_API_KEY` | Yes | API key from WakaTime or Wakapi. Sent on every request as **HTTP Basic** auth: `Authorization: Basic` + base64(key) only (no username). |
| `WAKAPI_URL` | No | Site **origin** (scheme + host; trailing `/` stripped). Unset ⇒ **`https://wakatime.com`**. Set for Wakapi / self-hosted (e.g. `https://wakapi.dev`). The key is sent to **this** host. **`status-bar`** always requests **`{origin}/api/v1/users/current/statusbar/today`**. Other subcommands use **`/api/v1`** only when the hostname is **exactly** `wakatime.com`; **any other host** (including Wakapi) uses **`/api/compat/wakatime/v1`** for those calls — see `scripts/wakatime_query.py` (`_compat_api_prefix`). |

Do not commit secrets. **No other environment variables** are read; use CLI flags (see below).

## Using & developing

For **contributors** or anyone running the CLI from a **git checkout** (not only as an installed skill folder).

### Clone the repository

Upstream:

```bash
git clone https://github.com/chensoul/wakapi-skill.git
cd wakapi-skill
```

SSH: `git clone git@github.com:chensoul/wakapi-skill.git`. If you use a **fork**, clone your fork’s URL instead.

### Python virtual environment (recommended)

The CLI uses **Python 3** and the **standard library only** — no `requirements.txt` is required to run or test.

```bash
python3 -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows cmd
# .venv\Scripts\Activate.ps1       # Windows PowerShell
```

`.venv/` is gitignored. CI uses **Python 3.11**; any recent 3.x should work.

**Optional — coverage** (for line coverage reports):

```bash
pip install coverage
```

### Run the CLI from the repo

Stay in the repo root (with venv activated if you use one). Set [configuration](#configuration) as usual:

```bash
export WAKAPI_API_KEY="your-key"
# optional: export WAKAPI_URL="https://your-wakapi.example"

python3 scripts/wakatime_query.py --help
python3 scripts/wakatime_query.py health
python3 scripts/wakatime_query.py projects
```

### Run tests

Tests use **`unittest`** and **`unittest.mock`** (they patch `urllib.request.urlopen`; **no real network**):

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Quiet run (e.g. in scripts):

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -q
```

### Code coverage (optional)

With `coverage` installed:

```bash
coverage run --source=scripts -m unittest discover -s tests -p 'test_*.py' -q
coverage report -m --include='scripts/wakatime_query.py'
```

`wakatime_query.py` is kept at **100%** line coverage; the `if __name__ == "__main__"` block uses `# pragma: no cover` because tests call `main()` via import.

### What to edit

| Area | Files |
|------|--------|
| CLI behavior / endpoints | `scripts/wakatime_query.py` |
| Agent-facing instructions | `SKILL.md`, `references/*.md` |
| Tests | `tests/test_wakatime_query.py` |

After changes, run **unittest** (and optionally **coverage**) before opening a PR.

## CI & publishing

Workflows mirror [wakapi-skill](https://github.com/chensoul/wakapi-skill/tree/main/.github/workflows):

| Workflow | When | What |
|----------|------|------|
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | Every push / PR | `py_compile`, `unittest`, **package-check** (rsync + [`.clawhubignore`](.clawhubignore)) |
| [`.github/workflows/release.yml`](.github/workflows/release.yml) | Push tag `v*` | Tarball + [GitHub Release](https://github.com/softprops/action-gh-release) |
| [`.github/workflows/clawhub-publish.yml`](.github/workflows/clawhub-publish.yml) | Tag `v*` or **workflow_dispatch** | Publish to ClawHub (`CLAWHUB_TOKEN` secret) |

ClawHub slug: **`wakapi-skill`**, display name: **Wakapi / WakaTime Query**.

**Registry metadata:** [`SKILL.md`](SKILL.md) frontmatter uses **`metadata.openclaw`**: **`requires.env`** is **`["WAKAPI_URL", "WAKAPI_API_KEY"]`** and **`primaryEnv`** is **`WAKAPI_API_KEY`**, plus **`homepage`** / **`repository`** ([ClawHub metadata & scanners](https://github.com/openclaw/clawhub/issues/522)). The **key is required**; **API URL is optional** (defaults to WakaTime cloud) — see the skill description for **HTTP Basic** usage.

## License

See [LICENSE](LICENSE).
