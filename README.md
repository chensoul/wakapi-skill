# wakapi-skill

Portable **agent skill** to query **WakaTime** or **Wakapi** coding stats via a small Python CLI. Works with any tool that loads `SKILL.md` skills (Cursor, Claude Code, OpenClaw, Codex, etc.).

**Repository:** [github.com/chensoul/wakapi-skill](https://github.com/chensoul/wakapi-skill)

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

## Install (examples)

**Cursor:** `~/.cursor/skills/wakapi-skill` or `<project>/.cursor/skills/wakapi-skill` (not `~/.cursor/skills-cursor/`).

**Claude Code:** `~/.claude/skills/wakapi-skill` or `<project>/.claude/skills/wakapi-skill` — see [Claude Code — Skills](https://code.claude.com/docs/en/skills).

## Configuration

| Variable | Required | Purpose |
|----------|----------|---------|
| `WAKAPI_API_KEY` | Yes | API key from WakaTime or Wakapi. |
| `WAKAPI_BASE_URL` | No | Leave unset for **WakaTime cloud** (`https://wakatime.com`). Set to e.g. `https://wakapi.dev` or self-hosted Wakapi if needed. **`status-bar`** always calls **`/api/v1/users/current/statusbar/today`**; other subcommands use **`/api/v1`** on WakaTime and **`/api/compat/wakatime/v1`** on other hosts (Wakapi). |

Do not commit secrets. **No other environment variables** are read; use CLI flags (see below).

### CLI

| Flag | Purpose |
|------|---------|
| `--debug` / `-d` | Print each request URL to **stderr**. May appear **anywhere** (before or after the subcommand), e.g. `projects -d`. |

Subcommands **`health`**, **`projects`**, **`status-bar`**, **`all-time-since`** accept **`--timeout SEC`** as **HTTP socket** timeout (defaults: **15** s for `health`, **60** s for the others).

**`stats`** / **`summaries`** use a fixed **60** s HTTP timeout. Their **`--timeout`** (where present) is a **WakaTime API query parameter** (keystroke timeout), not the HTTP client timeout — see `stats --help` / `summaries --help`.

Example: `python3 scripts/wakatime_query.py projects -d`

`.env` is not loaded automatically — use `export`, IDE env, or `set -a && source .env && set +a`.

## CI & publishing (maintainers)

Workflows mirror [wakapi-sync-skill](https://github.com/cosformula/wakapi-sync-skill/tree/main/.github/workflows):

| Workflow | When | What |
|----------|------|------|
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | Every push / PR | `py_compile`, `unittest`, **package-check** (rsync + [`.clawhubignore`](.clawhubignore)) |
| [`.github/workflows/release.yml`](.github/workflows/release.yml) | Push tag `v*` | Tarball + [GitHub Release](https://github.com/softprops/action-gh-release) |
| [`.github/workflows/clawhub-publish.yml`](.github/workflows/clawhub-publish.yml) | Tag `v*` or **workflow_dispatch** | Publish to ClawHub (`CLAWHUB_TOKEN` secret) |

ClawHub slug: **`wakapi-skill`**, display name: **Wakapi / WakaTime Query**.

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
# optional: export WAKAPI_BASE_URL="https://your-wakapi.example"

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

## Contents

| Path | Role |
|------|------|
| [SKILL.md](SKILL.md) | Agent instructions |
| [scripts/wakatime_query.py](scripts/wakatime_query.py) | CLI |
| [references/wakapi-api.md](references/wakapi-api.md) | Wakapi paths & auth (aligned with this CLI) |
| [references/wakatime-api.md](references/wakatime-api.md) | WakaTime cloud API (aligned with this CLI) |
| [tests/test_wakatime_query.py](tests/test_wakatime_query.py) | Unit tests (`unittest`, no network) |
| [.clawhubignore](.clawhubignore) | Excludes tests / README / `.github` from the ClawHub publish bundle (used by CI `rsync`) |
| [.gitattributes](.gitattributes) | Keeps `.clawhubignore` as **LF** line endings — **CRLF breaks** `rsync --exclude-from` on Linux/macOS |

## License

See [LICENSE](LICENSE).
