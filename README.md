# wakapi-skill

Portable **agent skill** for querying **WakaTime** or **WakaTime-compatible** APIs (e.g. self-hosted [Wakapi](https://github.com/muety/wakapi)) via `WAKAPI_BASE_URL` and `WAKAPI_API_KEY`.

It is **not tied to a single editor or vendor**: the same folder works anywhere that loads skills from a `SKILL.md` file with YAML frontmatter (e.g. **Cursor**, **Claude Code**, **OpenClaw**, **Codex**, and similar agents).

## Skill layout

This repository root **is** one skill directory:

```
wakapi-skill/
├── SKILL.md                 # required — instructions for the agent
├── references/
│   └── reference.md         # optional — endpoint cheat sheet
├── README.md                # human-oriented install & verify
├── scripts/
│   └── wakatime_query.py    # optional — Python CLI (stdlib only)
```

Copy or symlink the **whole directory** into your product’s skills location so the tool sees `…/wakapi-skill/SKILL.md`.

## Install by product

Paths vary by release; if these differ on your machine, follow your product’s official “skills” or “plugins” documentation.

### Cursor

- **Personal:** `~/.cursor/skills/wakapi-skill` (symlink or copy this repo there).
- **Project:** `<repo>/.cursor/skills/wakapi-skill`

```bash
mkdir -p ~/.cursor/skills
ln -s /path/to/wakapi-skill ~/.cursor/skills/wakapi-skill
```

Do not use `~/.cursor/skills-cursor/` — reserved for Cursor-built-in skills.

### Claude Code

Typically a **named folder** under a skills root, containing `SKILL.md`:

- **Global:** `~/.claude/skills/wakapi-skill`
- **Project:** `<repo>/.claude/skills/wakapi-skill`

```bash
mkdir -p ~/.claude/skills
ln -s /path/to/wakapi-skill ~/.claude/skills/wakapi-skill
```

See [Claude Code — Skills](https://code.claude.com/docs/en/skills) for current behavior and verification (e.g. listing loaded skills).

### OpenClaw, Codex, and other agents

Use the directory your tool expects for **markdown / SKILL.md-based** skills. Often this is a global or project-level `skills` folder; symlink this repo so the resolved path includes `SKILL.md` at `…/wakapi-skill/SKILL.md`. Consult that product’s docs if discovery fails.

## Configuration

| Variable | Description |
|----------|-------------|
| `WAKAPI_BASE_URL` | API origin, e.g. `https://wakatime.com` or your Wakapi URL. **No** trailing slash, **no** `/api/v1`. |
| `WAKAPI_API_KEY` | Your secret API key (WakaTime account API key or Wakapi token per your server docs). |
| `WAKAPI_BASIC_HEADER` | *(Optional)* Full `Authorization` header value (e.g. `Basic <base64>`). If set, the Python CLI uses it instead of deriving auth from `WAKAPI_API_KEY`. Same idea as Option C in [SKILL.md](SKILL.md) for `curl`. |

**Do not commit secrets.** Use a local `.env` (ignored by git) for your values.

**`.env` is not loaded automatically** by `scripts/wakatime_query.py` or by anything else in this repo. Variables must already be in the environment (shell `export`, CI secrets, Cursor/IDE env, [direnv](https://direnv.net/), etc.).

Example (interactive shell):

```bash
export WAKAPI_BASE_URL="https://wakatime.com"
export WAKAPI_API_KEY="your-secret-key"
```

Load a `.env` file into the current shell (bash-compatible):

```bash
set -a && source .env && set +a
```

## Verify

With variables set:

```bash
AUTH=$(printf '%s' "$WAKAPI_API_KEY" | base64 | tr -d '\n')
curl -sS -w "\nHTTP %{http_code}\n" \
  -H "Authorization: Basic ${AUTH}" \
  "${WAKAPI_BASE_URL}/api/v1/users/current/projects"
```

Expect HTTP `200` and a JSON body.

## Python CLI (optional)

[`scripts/wakatime_query.py`](scripts/wakatime_query.py) calls the same five API areas using **`WAKAPI_BASE_URL`** plus **`WAKAPI_API_KEY`** (unless **`WAKAPI_BASIC_HEADER`** is set). **Standard library only** — no `pip install`.

From the skill/repo root (with env vars set):

```bash
python3 scripts/wakatime_query.py --help
python3 scripts/wakatime_query.py health
python3 scripts/wakatime_query.py projects
```

## Contents

| File | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | Agent instructions (endpoints, auth, curl, errors) |
| [references/reference.md](references/reference.md) | Parameter cheat sheet + doc links |
| [scripts/wakatime_query.py](scripts/wakatime_query.py) | Optional Python CLI (stdlib) |

## Plan checklist (实现核对)

Original skill plan items — all covered in this repo:

| Item | Location |
|------|----------|
| Root `SKILL.md` (frontmatter, auth, 5 endpoints, curl, errors, Wakapi note) | [SKILL.md](SKILL.md) |
| Endpoint / parameter cheat sheet + doc links | [references/reference.md](references/reference.md) |
| Human install (multi-product), env vars, verify `curl` | This README |
| Ignore `.env` / `.env.*` for local secrets | [.gitignore](.gitignore) |
| Optional Python helper | [scripts/wakatime_query.py](scripts/wakatime_query.py) |

## License

See [LICENSE](LICENSE).
