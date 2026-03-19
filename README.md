# wakapi-skill

[![ClawHub](https://img.shields.io/badge/ClawHub-wakapi--skill-blue)](https://clawhub.ai/skills/wakapi-skill)
[![ClawHub version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fclawhub.ai%2Fapi%2Fv1%2Fskills%2Fwakapi-skill&query=%24.skill.tags.latest&label=clawhub&prefix=v&color=blue)](https://clawhub.ai/skills/wakapi-skill)
[![ClawHub downloads](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fclawhub.ai%2Fapi%2Fv1%2Fskills%2Fwakapi-skill&query=%24.skill.stats.downloads&label=clawhub%20downloads&color=blue)](https://clawhub.ai/skills/wakapi-skill)
[![GitHub stars](https://img.shields.io/github/stars/chensoul/wakapi-skill?style=flat&logo=github)](https://github.com/chensoul/wakapi-skill)
[![License](https://img.shields.io/github/license/chensoul/wakapi-skill)](./LICENSE)
[![Publish to ClawHub](https://github.com/chensoul/wakapi-skill/actions/workflows/clawhub-publish.yml/badge.svg)](https://github.com/chensoul/wakapi-skill/actions/workflows/clawhub-publish.yml)

Portable **agent skill** for **Wakapi**: read-only coding stats via a small Python CLI (`WAKAPI_URL`, `WAKAPI_API_KEY`).

## Documentation

| File | Contents |
|------|----------|
| **[SKILL.md](SKILL.md)** | When to use, env, **subcommand table**, grouped CLI examples |
| **[references/wakapi-api.md](references/wakapi-api.md)** | URLs, auth, **`stats` vs `summaries`**, Wakapi **`--range`** semantics, **curl**, timeouts |

## Layout

```
wakapi-skill/
├── SKILL.md                 
├── README.md
├── LICENSE
├── references/
│   └── wakapi-api.md
├── scripts/
│   └── wakapi_query.py
├── tests/
│   └── test_wakapi_query.py
```

## Configuration

| Variable | Required | Purpose |
|----------|----------|---------|
| `WAKAPI_URL` | Yes | Instance **origin** (e.g. `https://wakapi.dev`). |
| `WAKAPI_API_KEY` | Yes* | API key (**HTTP Basic**, key only). *Not required for **`health`** (`GET /api/health`). |

Do not commit secrets. **No other environment variables** are read; use CLI flags (see `SKILL.md`).

## Using & developing

### Clone

```bash
git clone https://github.com/chensoul/wakapi-skill.git
cd wakapi-skill
```

### Virtualenv (optional)

Python **3.x**, **stdlib only**.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Run CLI

```bash
# Instance origin + API key (key not needed only for `health`)
export WAKAPI_URL="https://your-wakapi.example"
export WAKAPI_API_KEY="your-key"

python3 scripts/wakapi_query.py --help
python3 scripts/wakapi_query.py health                    # GET /api/health
python3 scripts/wakapi_query.py summaries --range today   # compat summaries ?range=
python3 scripts/wakapi_query.py summaries --range last_7_days --timezone Asia/Shanghai
```

More examples: **[SKILL.md](SKILL.md)** · API details: **[references/wakapi-api.md](references/wakapi-api.md)**.

### Tests

Wakapi:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

### Coverage (optional)

```bash
pip install coverage
coverage run --source=scripts -m unittest discover -s tests -p 'test_*.py' -q
coverage report -m --include='scripts/wakapi_query.py'
```

### What to edit

| Area | Files |
|------|--------|
| Wakapi CLI | `scripts/wakapi_query.py` |
| Agent docs | `SKILL.md`, `references/wakapi-api.md`, … |
| Tests | `tests/test_wakapi_query.py` |

## CI & publishing

| Workflow | When | What |
|----------|------|------|
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | Push / PR | `py_compile`, `unittest`, **package-check** (publish dir = Wakapi skill only; see `.clawhubignore`) |
| [`.github/workflows/release.yml`](.github/workflows/release.yml) | Tag `v*` | Tarball |
| [`.github/workflows/clawhub-publish.yml`](.github/workflows/clawhub-publish.yml) | Tag / dispatch | Publish **`wakapi-skill`** to ClawHub |

ClawHub slug: **`wakapi-skill`**. Registry metadata: [`SKILL.md`](SKILL.md).

## License

See [LICENSE](LICENSE).
